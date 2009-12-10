'''
Serialize a django form instance into JSON
'''
from djpcms.utils import json
from django.db import models
from django.db.models import query


def dumps(atom):
    if isinstance(atom,models.Model):
        return atom.pk
    elif isinstance(atom, query.QuerySet):
        return [elem.id for elem in atom]
    else:
        return atom

def form2json(form):
    if form and form.is_valid():
        data = form.cleaned_data
        fields = {}
        for k,v in data.items():
            fields[k] = dumps(v)
        return json.dumps(fields)
    else:
        return u''
