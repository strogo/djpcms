from django.db.models.base import ModelBase
from django.forms.models import model_to_dict
from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.admin import site
from django.contrib.admin.util import label_for_field, display_for_field, lookup_field

from django.db.models import Q
from django.db.models.query import QuerySet
from django.utils.text import smart_split

from djpcms import sites
from djpcms.permissions import has_permission
from djpcms.utils import force_str
from djpcms.template import mark_safe, escape, conditional_escape

from .base import ModelTypeWrapper, _boolean_icon, nicerepr


class ModelType(ModelTypeWrapper):
    '''Wrapper for django models'''
    def setup(self):
        model_admin = site._registry.get(self.model,None)
        self.model_admin = model_admin
        self.meta = self.model._meta
        self.module_name = self.meta.module_name
        self.app_label   = self.meta.app_label
        appmodel = self.appmodel
        list_display = appmodel.list_display
        list_display_links = appmodel.list_display_links
        search_fields = appmodel.search_fields
        if list_display is None:
            if model_admin:
                list_display = model_admin.list_display
            else:
                list_display = []
        if list_display_links is None:
            if model_admin:
                list_display_links = model_admin.list_display_links
            else:
                list_display_links = []
        if search_fields is None:
            if model_admin:
                search_fields = model_admin.search_fields
            else:
                search_fields = []
        self.list_display = list_display
        self.list_display_links = list_display_links
        self.search_fields = search_fields
    
    def has_add_permission(self, user, obj=None):
        return has_permission(user, self.get_add_permission(), obj)
    
    def has_change_permission(self, user, obj=None):
        return has_permission(user, self.get_change_permission(), obj)
    
    def has_view_permission(self, user, obj = None):
        return has_permission(user, self.get_view_permission(), obj)
    
    def has_delete_permission(self, user, obj=None):
        return has_permission(user, self.get_delete_permission(), obj)
    
    def get_view_permission(self):
        return '%s_view' % self.meta
    
    def get_add_permission(self):
        opts = self.meta
        return opts.app_label + '.' + opts.get_add_permission()
    
    def get_change_permission(self):
        opts = self.meta
        return opts.app_label + '.' + opts.get_change_permission()
    
    def get_delete_permission(self):
        opts = self.meta
        return opts.app_label + '.' + opts.get_delete_permission()
        
    def _label_for_field(self, name):
        return label_for_field(name, self.model, self.model_admin)

    def test(self, model):
        if not isinstance(model,ModelBase):
            raise ValueError
        
    def _getrepr(self, name, instance):
        try:
            f, attr, value = lookup_field(name, instance, self.model_admin)
        except (AttributeError, ObjectDoesNotExist):
            result_repr = self.get_value(instance, name, sites.settings.DJPCMS_EMPTY_VALUE)
        else:
            if f is None:
                allow_tags = getattr(attr, 'allow_tags', False)
                boolean = getattr(attr, 'boolean', False)
                if boolean:
                    allow_tags = True
                    result_repr = _boolean_icon(value)
                else:
                    result_repr = force_str(value)
                # Strip HTML tags in the resulting text, except if the
                # function has an "allow_tags" attribute set to True.
                if not allow_tags:
                    result_repr = escape(result_repr)
                else:
                    result_repr = mark_safe(result_repr)
            else:
                if value is None:
                    result_repr = sites.settings.DJPCMS_EMPTY_VALUE
                if isinstance(f.rel, models.ManyToOneRel):
                    result_repr = escape(getattr(instance, f.name))
                else:
                    result_repr = display_for_field(value, f)
        return result_repr
    
    def model_to_dict(self, instance, fields = None, exclude = None):
        raise model_to_dict(instance, fields, exclude)
