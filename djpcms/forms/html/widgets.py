from djpcms.utils import merge_dict

from .base import HtmlWidget


__all__ = ['TextInput',
           'SubmitInput',
           'HiddenInput',
           'PasswordInput']

class TextInput(HtmlWidget):
    tag = 'input'
    inline = True
    attributes = merge_dict(HtmlWidget.attributes, {
                                                    'type':'text',
                                                    'value': None,
                                                    'name': None
                                                    })
    
class SubmitInput(TextInput):
    attributes = merge_dict(TextInput.attributes, {'type':'submit'})
    
    
class HiddenInput(TextInput):
    is_hidden = True
    attributes = merge_dict(TextInput.attributes, {'type':'hidden'})
    
    
class PasswordInput(TextInput):
    attributes = merge_dict(TextInput.attributes, {'type':'password'})