from djpcms.markups import addmarkup

from djpcms.tools import creole

if creole.available:
    addmarkup('crl',u'Creole',creole.text2html)
#addmarkup('tex',u'Latex',latex.text2html)