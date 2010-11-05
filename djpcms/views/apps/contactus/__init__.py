from djpcms.views import appsite, appview

from contactform import ContactForm


class ContactView(appview.AppViewBase):
    
    def get_form(self, djp):
        return self.appmodel.get_form(djp)
        
    def render(self, djp, **kwargs):
        return self.get_form(djp).render()
    
    def default_post(self, djp):
        return appview.saveform(self, djp)
    
    def save(self, request, f):
        return f.save()
    
    def success_message(self, instance, flag):
        return "Your message has been sent. Thank you!"


class ContactUs(appsite.ApplicationBase):
    name = 'Contact Us'
    form = ContactForm
    form_withrequest = True
    contact = ContactView(isplugin = True)