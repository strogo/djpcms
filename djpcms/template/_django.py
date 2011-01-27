from django.utils import safestring
from django.utils import html
from django.template import loader, Context, Template
from django.template import context

from .base import LibraryTemplateHandler


class TemplateHandler(LibraryTemplateHandler):
    
    def setup(self):
        self.mark_safe = safestring.mark_safe
        self.template_class = Template
        self.context_class = Context
        self.escape = html.escape
        self.conditional_escape = html.conditional_escape
        self.get_processors = context.get_standard_processors
        
    def get_template(self, template_name):
        if isinstance(template_name, (list, tuple)):
            return loader.select_template(template_name)
        else:
            return loader.get_template(template_name)
        
    def render_to_string(self, template_name, dictionary=None, context_instance=None):
        dictionary = dictionary or {}
        t = self.get_template(template_name)
        if context_instance:
            context_instance.update(dictionary)
        else:
            context_instance = Context(dictionary)
        return t.render(context_instance)

    def render(self, template_name, dictionary=None, autoescape = False):
        context_instance = Context(dictionary, autoescape = autoescape)
        t = self.get_template(template_name)
        return t.render(context_instance)
