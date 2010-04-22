from django import template

register = template.Library()

class_converter = {
    "textinput":"textinput textInput",
    "fileinput":"fileinput fileUpload",
    "datetimeinput": "datetimeinput textInput",
    "dateinput": "dateinput textInput"
}

def get_class_name(field):
    widget_class = getattr(field.field.widget,'class_for_form',field.field.widget.__class__)
    return widget_class.__name__.lower()

@register.filter
def is_checkbox(field):
    return get_class_name(field) == "checkboxinput"

@register.filter
def with_class(field):
    class_name = get_class_name(field)
    class_name = class_converter.get(class_name, class_name)
    if "class" in field.field.widget.attrs:
        field.field.widget.attrs['class'] += " %s" % class_name
    else:
        field.field.widget.attrs['class'] = class_name
    return unicode(field)