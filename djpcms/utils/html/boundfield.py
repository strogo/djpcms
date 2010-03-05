from django.utils.encoding import StrAndUnicode, smart_unicode, force_unicode
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django import forms

from djpcms.conf import settings


__all__ = ['BoundField','ErrorList']


class ErrorList(forms.util.ErrorList):
    
    def __unicode__(self):
        return self.as_li()
    
    def as_li(self):
        if not self: return u''
        return mark_safe(u'%s' % ''.join([u'<li>%s</li>' % force_unicode(e) for e in self]))


class BoundField(object):
    ajax = settings.HTML_CLASSES
    '''
    Wrapper for django Forms BoundField
    '''
    def __init__(self, bfield, form, editinline = False):
        self.field  = bfield
        self.widget = bfield.field.widget
        self.form   = form
        self.is_checkbox = isinstance(self.widget, forms.CheckboxInput)
    
    def label_tag(self):
        classes = []
        if self.is_checkbox:
            classes.append(u'vCheckboxLabel')
            contents = force_unicode(escape(self.field.label))
        else:
            contents = force_unicode(escape(self.field.label)) + u':'
        if self.field.field.required:
            classes.append(u'required')
        attrs = classes and {'class': u' '.join(classes)} or {}
        return self.field.label_tag(contents=contents, attrs=attrs)
    
    def id(self):
        return self.widget.attrs.get('id') or self.field.auto_id
    
    def errorid(self):
        '''
        error's id
        '''
        return 'error_%s' % self.id()

    def __unicode__(self):
        """Renders this field as an HTML widget."""
        return self.as_widget()

    def _errors(self):
        """
        Returns an ErrorList for this field. Returns an empty ErrorList
        if there are none.
        """
        return self.form.errors.get(self.name, self.ajax.errorlist)
    errors = property(_errors)
    
    def datavalue(self):
        if not self.form.is_bound:
            data = self.form.initial.get(self.name, self.field.initial)
            if callable(data):
                data = data()
        else:
            data = self.data
        return data

    def as_widget(self, widget=None, attrs=None):
        """
        Renders the field by rendering the passed widget, adding any HTML
        attributes passed as attrs.  If no widget is specified, then the
        field's default widget will be used.
        """
        if not widget:
            widget = self.field.widget
        attrs = attrs or {}
        auto_id = self.auto_id
        if auto_id and 'id' not in attrs and 'id' not in widget.attrs:
            attrs['id'] = auto_id
        data = self.datavalue()
        return widget.render(self.html_name, data, attrs=attrs)

    def as_text(self, attrs=None):
        """
        Returns a string of HTML for representing this as an <input type="text">.
        """
        return self.as_widget(TextInput(), attrs)

    def as_textarea(self, attrs=None):
        "Returns a string of HTML for representing this as a <textarea>."
        return self.as_widget(Textarea(), attrs)

    def as_hidden(self, attrs=None):
        """
        Returns a string of HTML for representing this as an <input type="hidden">.
        """
        return self.as_widget(self.field.hidden_widget(), attrs)

    def _data(self):
        """
        Returns the data for this BoundField, or None if it wasn't given.
        """
        return self.field.widget.value_from_datadict(self.form.data, self.form.files, self.html_name)
    data = property(_data)


    def _is_hidden(self):
        "Returns True if this BoundField's is hidden."
        return self.field.is_hidden
    is_hidden = property(_is_hidden)

    def _auto_id(self):
        """
        Calculates and returns the ID attribute for this BoundField, if the
        associated Form has specified auto_id. Returns an empty string otherwise.
        """
        auto_id = self.form.auto_id
        if auto_id and '%s' in smart_unicode(auto_id):
            return smart_unicode(auto_id) % self.html_name
        elif auto_id:
            return self.html_name
        return ''
    auto_id = property(_auto_id)
    
    def errordiv(self):
        return u'''<div id="%s" class="%s"></div>''' % (self.errorid(),self.ajax.errorlist)
    
    def helpdiv(self):
        return u'''<div class="help-text">%s</div>''' % self.field.help_text
    
    def as_tablerow2(self):
        html = [u'''<tr>''',
                u'''<td align="left">%s</td>''' % self.label_tag(),
                u'''<td align="left">%s</td>''' % force_unicode(self.field),
                u'''</tr>''']
        if self.field.help_text:
            h = [u'''<tr>''',
                 u'''<td align="left"></td>''',
                 u'''<td align="left">''',
                 self.helpdiv(),
                 u'''</td>'''
                 u'''</tr>''']
            html.extend(h)
        h = [u'''<tr>''',
             u'''<td align="left"></td>''',
             u'''<td align="left">''',
             self.errordiv(),
             u'''</td>'''
             u'''</tr>''']
        html.extend(h)
        return mark_safe(u'\n'.join(html))
    
    def as_tablerow12(self):
        return self.as_tablerow1(2)

    def as_tablerow1(self, cs = 1):
        csm = 'colspan = "%s"' % cs
        html = [u'''<tr>''',
                u'''<td align="left" %s>%s</td>''' % (csm,self.label_tag()),
                u'''</tr>''',
                u'''<tr>''',
                u'''<td %s>''' % csm,
                self.errordiv(),
                u'''</td>''',
                u'''</tr>''',
                u'''<tr>''',
                u'''<td align="left" %s>%s</td>''' % (csm,force_unicode(self.field)),
                u'''</tr>''']
        if self.field.help_text:
            h = [u'''<tr>''',
                 u'''<td align="left" %s>''' % csm,
                 self.helpdiv(),
                 u'''</td>'''
                 u'''</tr>''']
            html.extend(h)
        return mark_safe(u'\n'.join(html))
    
    def as_divs(self):
        html = ['''<div>%s</div>''' % self.label_tag(),
                self.errordiv(),
                '''<div>%s</div>''' % force_unicode(self.field)]
        if self.field.help_text:
            html.append(self.helpdiv())
        return mark_safe(u'\n'.join(html))
    
    def as_divnolabel(self):
        html = [self.errordiv(),
                '''<div>%s</div>''' % force_unicode(self.field)]
        if self.field.help_text:
            html.append(self.helpdiv())
        return mark_safe(u'\n'.join(html))