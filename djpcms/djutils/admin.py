
from django.contrib import admin


class ModelAdminRequest(admin.ModelAdmin):
    
    def get_form(self, request, obj=None, **kwargs):
        """
        Returns a Form class for use in the admin add view. This is used by
        add_view and change_view.
        """
        if self.declared_fieldsets:
            fields = flatten_fieldsets(self.declared_fieldsets)
        else:
            fields = None
        if self.exclude is None:
            exclude = []
        else:
            exclude = list(self.exclude)
        # if exclude is an empty list we pass None to be consistant with the
        # default on modelform_factory
        defaults = {
            "form": self.form,
            "fields": fields,
            "exclude": (exclude + kwargs.get("exclude", [])) or None,
            "formfield_callback": curry(self.formfield_for_dbfield, request=request),
            "request": request
        }
        defaults.update(kwargs)
        return modelform_factory(self.model, **defaults)
    