'''
Serialize a django form instance into JSON
'''
from djpcms.utils import json
from django.db import models


def dumps(atom):
    if isinstance(atom,models.Model):
        return atom.pk
    else:
        return atom

def form2json(form):
    if form.is_valid():
        data = form.cleaned_data
        fields = {}
        for k,v in data.items():
            fields[k] = dumps(v)
        return json.dumps(fields)
    else:
        return u''
