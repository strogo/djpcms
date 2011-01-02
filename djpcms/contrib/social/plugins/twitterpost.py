from djpcms import forms
from djpcms.utils.uniforms import FormLayout, Fieldset, nolabel
from djpcms.utils.ajax import jhtmls
from djpcms.contrib.social.applications import SocialActionPlugin


class MessageForm(forms.Form):
    message = forms.CharField(widget = forms.Textarea(attrs = {'class':'twitter-box-editor'}))
    submits = (('tweet','tweet'),)
    layout = FormLayout(Fieldset('message',css_class=nolabel))


class TwitterPostMessage(SocialActionPlugin):
    provider_name = 'twitter'
    action_name   = 'post-message'
    description   = 'twitter messaging'
    
    def get_form(self, djp):
        return djp.view.get_form(djp,
                                 form = MessageForm,
                                 form_ajax = True)
                                 
    def _render(self, djp):
        return self.get_form(djp).render(djp)
        
    def handle_post(self, djp, api, user_data):
        f = self.get_form(djp)
        if not f.is_valid():
            return djp.view.error_post(djp,'Error in form')
        msg  = f.cleaned_data['message']
        api.update_status(msg)
        return jhtmls(identifier = '.twitter-box-editor', html = '', type = 'value')
    