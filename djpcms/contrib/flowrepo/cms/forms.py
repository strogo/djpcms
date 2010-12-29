from django.contrib.auth.models import User

from djpcms.contrib.flowrepo import markups
from djpcms.contrib.flowrepo.models import FlowItem, Attachment, Image
from djpcms.contrib.flowrepo.forms import WebAccountForm, UploadForm, FlowForm, ReportForm

from djpcms import forms
from djpcms.utils.uniforms import FormLayout, Fieldset, Html, inlineLabels, blockLabels2
from djpcms.utils.html import htmlwrap, box
from djpcms.views.apps.tagging import Tag, TagField


CRL_HELP = htmlwrap('div',
                    htmlwrap('div',markups.help()).addClass('body').render()
                   ).addClasses('flowitem report').render()


collapse = lambda title, html, c, cl: box(hd = title, bd = html, collapsable = c, collapsed = cl)


__all__ = ['FlowForm','NiceWebAccountForm','NiceUloaderForm','NiceReportForm']



#_________________________________________________________ UNIFORMS

class NiceWebAccountForm(WebAccountForm):
    
        # add the layout object
    layout = FormLayout(Fieldset('name', 'url', 'tags', css_class = blockLabels2),
                        Fieldset('username', 'password', 'email','pin', css_class = blockLabels2)
                        )
    
    
class NiceUloaderForm(UploadForm):
    
    layout = FormLayout(Fieldset('visibility', 'tags', 'name', css_class = inlineLabels),
                                 Fieldset('elem','description', css_class = blockLabels2),
                        )
    
    
class NiceReportForm(ReportForm):
    authors  = forms.ModelMultipleChoiceField(User.objects.all(), required = False)
    related_items = forms.ModelMultipleChoiceField(queryset = FlowItem.objects.all(),
                                                   required = False,
                                                   label = 'Connect the write-up with other items')
    
    layout = FormLayout(
                             Fieldset('title', 'abstract', 'body', key = 'body'),
                    
                             Fieldset('visibility', 'allow_comments', css_class = inlineLabels),
                            
                             Fieldset('tags', 'authors', css_class = blockLabels2),
                             
                             Fieldset('related_items',
                                      css_class = blockLabels2,
                                      key = 'related_items',
                                      renderer = lambda html : collapse('Related Items',html,True,False)),
                                      
                             Fieldset('slug', 'timestamp', 'markup',
                                      key = 'metadata',
                                      renderer = lambda html : collapse('Metadata',html,True,True)),
                                      
                             Html(CRL_HELP, key = 'help',
                                      renderer = lambda html : collapse('Writing Tips',html,True,True)),
                    
                             template = 'flowrepo/report-form-layout.html')

    class Media:
        js = ('djpcms/taboverride.js',)

    