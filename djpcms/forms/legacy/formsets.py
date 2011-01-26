from django.forms.formsets import BaseFormSet, all_valid
from django.forms.formsets import formset_factory
from django.forms.models import _get_foreign_key
from django.forms.models import BaseModelFormSet, BaseInlineFormSet

from forms import ModelForm, modelform_factory


def modelformset_factory(model, form=ModelForm, formfield_callback=None,
                         formset=BaseModelFormSet,
                         extra=1, can_delete=False, can_order=False,
                         max_num=None, fields=None, exclude=None):
    """
    Returns a FormSet class for the given Django model class.
    """
        
    form = modelform_factory(model, form=form, fields=fields, exclude=exclude,
                             formfield_callback=formfield_callback)
    FormSet = formset_factory(form, formset, extra=extra, max_num=max_num,
                              can_order=can_order, can_delete=can_delete)
    FormSet.model = model
    return FormSet


def inlineformset_factory(parent_model,
                          model,
                          extra=3,
                          max_num=None,
                          fk_name=None,
                          formset=BaseInlineFormSet,
                          **kwargs):
    """
    Returns an ``InlineFormSet`` for the given kwargs.

    You must provide ``fk_name`` if ``model`` has more than one ``ForeignKey``
    to ``parent_model``.
    """
    # enforce a max_num=1 when the foreign key to the parent model is unique.
    fk = _get_foreign_key(parent_model, model, fk_name=fk_name)
    if fk.unique:
        max_num = 1
    FormSet = modelformset_factory(model,
                                   formset=formset,
                                   max_num=max_num,
                                   extra=extra,
                                   **kwargs)
    FormSet.fk = fk
    return FormSet

