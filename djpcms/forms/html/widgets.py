from djpcms.utils import merge_dict

from .base import HtmlWidget


__all__ = ['TextInput',
           'SubmitInput',
           'HiddenInput']

class TextInput(HtmlWidget):
    attributes = merge_dict(HtmlWidget.attributes, {
                                                    'type':'text',
                                                    'value': None,
                                                    'name': None
                                                    })
    
class SubmitInput(TextInput):
    attributes = merge_dict(TextInput.attributes, {'type':'submit'})
    
    
class HiddenInput(TextInput):
    attributes = merge_dict(TextInput.attributes, {'type':'hidden'})
    