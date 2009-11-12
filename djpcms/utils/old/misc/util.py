

def django_choices(vals):
    '''
    vals is an iterable
    '''
    choices = []
    if isinstance(vals,dict):
        for k,v in vals.iteritems():
            choices.append((str(k),str(v)))
    else:
        try:
            for v in vals:
                sv = str(v)
                choices.append((sv,sv))
        except:
            pass
    return choices

def dict_from_choices(cho):
    di = {}
    for c in cho:
        di[c[0]] = c[1]
    return di
                           
