# Requires flowrepo (not yet released)
#
from django.template import loader

from djpcms.plugins import DJPplugin
from djpcms.utils.html import htmlwrap, Paginator
from djpcms.views.apps.flowrepo.forms import ChangeCategory, ChangeImage

from flowrepo.models import FlowRelated, FlowItem, Report, Message, Category, Image
from flowrepo.forms import FlowItemSelector


class FlowItemSelection(DJPplugin):
    name = 'flowitem-selection'
    description = 'Items Selection'
    form = FlowItemSelector
    
    def render(self, djp, wrapper, prefix,
               visibility = None, item_per_page = 10,
               content_type = None, tags = '',
               **kwargs):
        request = djp.request
        qs      = FlowItem.objects.selection(request.user,
                                             types = content_type,
                                             visibility = visibility,
                                             tags = tags)
        if not qs:
            return None
        pa = Paginator(djp.request, qs, item_per_page)
        return loader.render_to_string(['flowitem_list.html',
                                        'djpcms/components/object_list.html'],
                                        {'items': self.paginator(djp,pa)})
        
    def paginator(self, djp, pa):
        from djpcms.views import appsite
        appmodel  = appsite.site.for_model(FlowItem)
        qs        = pa.qs
        for obj in qs:
            object    = obj.object
            model     = object.__class__
            objmodel  = appsite.site.for_model(model) or appmodel
            if objmodel:
                content = objmodel.object_content(djp, obj)
                tname   = '%s_list_item.html' % model.__name__.lower()
                yield loader.render_to_string(['components/%s' % tname,
                                               'flowrepo/%s' % tname,
                                               'flowrepo/flowitem_list_item.html'],
                                               content)


class ImagePlugin(DJPplugin):
    '''
    Plugin for displaying a single image on a content block
    '''
    name = 'image'
    description = 'Image'
    form = ChangeImage
    
    def render(self, djp, wrapper, prefix, image = None, class_name = None, **kwargs):
        try:
            img = Image.objects.get(id = int(image))
            if class_name:
                class_name = '%s image-plugin'
            else:
                class_name = 'image-plugin'
            cn = ' class="%s"' % class_name
            return '<img src="%s" title="%s" alt="%s"%s/>' % (img.url,img.name,img.name,cn)
        except:
            return u''
    

class CategoryLinks(DJPplugin):
    name = 'category-links'
    description = "Display links for a category"
    form          = ChangeCategory
    
    def render(self, djp, wrapper, prefix, category_name = None, **kwargs):
        if category_name:
            qs = Category.objects.filter(type__id = int(category_name))
        else:
            return u''
        if not qs:
            return u''
        return loader.render_to_string(['category_list.html',
                                        'components/category_list.html',
                                        'flowrepo/category_list.html'],
                                        {'items': self.paginator(djp,qs)})
    
    def paginator(self, djp, qs):
        from djpcms.views import appsite
        appmodel = appsite.site.for_model(Category)
        for obj in qs:
            if appmodel:
                content  = appmodel.object_content(djp, obj)
                yield loader.render_to_string(['category_list_item.html',
                                               'components/category_list_item.html',
                                               'flowrepo/category_list_item.html'],
                                               content)
        
    def edit_form(self, djp, category_name = None, **kwargs):
        if category_name:
            return EditContentForm(**form_kwargs(request = djp.request,
                                                 initial = {'category_name': category_name},
                                                 withrequest = True))


class LinkedItems(DJPplugin):
    '''
    Very very useful plugin for displaying a list of linked item
    to the flowitem object
    '''
    name = 'flowrepo-linked'
    description = "Linked item urls"
    
    def render(self, djp, wrapper, prefix, **kwargs):
        from djpcms.views import appsite
        instance = djp.instance
        if not isinstance(instance,FlowItem):
            return
        qs = FlowRelated.objects.filter(item = instance)
        if not qs:
            return
        request = djp.request
        return loader.render_to_string(['report_draft_list.html',
                                        'flowrepo/report_draft_list.html'],
                                        {'items': self.paginator(djp,qs)})
        
    def paginator(self, djp, qs):
        for obj in qs:
            object  = obj.object
            url     = object.url
            link    = htmlwrap('a', object.name)
            link._attrs['title'] = object.name
            link._attrs['href'] = url
            if not url.startswith('/'):
                link._attrs['target'] = "_blank"
            yield link.render()


class AddLinkedItems(DJPplugin):
    name = 'flowrepo-add-linked'
    description = "Add Linked item urls"
    
    def render(self, djp, wrapper, prefix, **kwargs):
        from djpcms.views import appsite
        instance = djp.instance
        if not isinstance(instance,FlowItem):
            return
        qs = FlowRelated.objects.filter(item = instance)
        if not qs:
            return
        request = djp.request
        return loader.render_to_string(['report_draft_list.html',
                                        'flowrepo/report_draft_list.html'],
                                        {'items': self.paginator(djp,qs)})
