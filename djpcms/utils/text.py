from .strings import force_str

def capfirst(x):
    x = force_str(x).strip()
    if x:
        return x[0].upper() + x[1:]
    else:
        return x

nicename = lambda name : force_str(capfirst(name.replace('-',' ').replace('_',' ')))


