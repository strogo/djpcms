from base import div
from table import table

gridc = 'djgrid-'

class yuigrid(div):
    '''
    YUI Nesting Grids layout.
    It splites the element into two columns with
    five different possibilities:
    
        layout = 'g'     (1/2 - 1/2)    default layout
                 'gc'    (2/3 - 1/3)
                 'gd'    (1/3 - 2/3)
                 'ge'    (3/4 - 1/4)
                 'gf'    (1/4 - 3/4)
        
    YUI grids:    http://developer.yahoo.com/yui/grids/
    '''
    def __init__(self, **attrs):
        layout = attrs.pop('layout','g')
        self.addclass('yui-%s' % layout)
        self['left']  = div(cn = 'yui-u first')
        self['right'] = div(cn = 'yui-u')


class oneandtwo(table):
    '''
    The table layout looks like this
    
    ---------------
    |             |
    |             |
    --------------|
    |      |      |
    |      |      |    
    |      |      |
    ---------------
    
    A right column and a left column with a top panel
    and two columns at the bottom.
    '''
    def __init__(self, baseclass = None):
        super(twoandthree,self).__init__(cols = 2)
        bc = baseclass or gridc
        self.addrow(div(cn = bc+'11'), colspan = 2)
        self.addrow(div(cn = bc+'21'), div(cn = bc+'22'))



class twoandthree(table):
    '''
    The table layout looks like this
    
    ----------------
    |         |    |
    |         |    |
    ----------|    |
    |    |    |    |
    |    |    |    |    
    |    |    |    |
    ----------------
    
    A right column and a left column with a top panel
    and two columns at the bottom.
    '''
    def __init__(self, baseclass = None):
        super(twoandthree,self).__init__(cols = 2)
        # Create the left table
        bc = baseclass or gridc
        self.addrow()
        
    
    