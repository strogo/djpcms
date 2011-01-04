from djpcms.contrib.medplate.css import CssContext

defaults = { 
    'background': '#fff',
    'color': '#000',
    'edit_background': '#f5f5f5',
    'edit_color': '#000',
    #
    #
    'font_family': "Helvetica,Arial,'Liberation Sans',FreeSans,sans-serif",
    'font_size': '14px',
    'font_weight': 'normal',
    'font_style': 'normal',
    'line_height': '1.3em',
    'text_align': 'left',
    #
    'anchor_weight':'normal',
    }
   
    
base_context = CssContext('body',
                          tag = 'body',
                          data = defaults,
                          template = 'medplate/base.css_t',
                          ineritable_tag = False)
context = base_context


context.add(
            CssContext('breadcrumbs',
                       tag = 'div.breadcrumbs',
                       template = 'medplate/breadcrumbs.css_t',
                       data = {
                               'font_size': '130%',
                               'padding': '10px 0'}
                       )
            )
                    

context.add(
            CssContext('nav',
                       tag='ul.main-nav',
                       template='medplate/horizontal_navigation.css_t',
                       data = {
                               'hover_background':'transparent',
                               'height': '2.5em',
                               'padding': 0,
                               'inner_height': '2.5em',
                               'list_margin': '0',
                               'secondary_width': '100px'}
                       )
            )


context.add(
            CssContext('tags',
                       tag='div.tagindex',
                       template='medplate/tags.css_t',
                       data = {
                               'text_align': 'justify'}
                       )
            )

context.add(
            CssContext('object_definitions',
                       tag='div.object-definition',
                       template='medplate/object-definition.css_t'
                       )
            )


context.add(
            CssContext('box',
                       tag='div.djpcms-html-box',
                       template='medplate/box/box.css_t',
                       elems = [CssContext('hd',
                                           tag='div.hd',
                                           data={'background':'transparent',
                                                 'padding':'5px 5px',
                                                 'overflow':'hidden'}),
                                CssContext('bd',
                                           tag='div.bd',
                                           data={'background':'transparent',
                                                 'padding':'5px 5px'}),
                                CssContext('ft',
                                           tag='div.ft',
                                           data={'background':'transparent',
                                                 'padding':'5px 5px',
                                                 'overflow':'hidden'})]
                       )
            )


context.add(
            CssContext('element',
                       tag='div.flat-element',
                       data = {'overflow':'hidden',
                               'padding':0}
                       )
            )

context.add(
            CssContext('panel',
                       tag='div.flat-panel',
                       data = {'overflow':'hidden',
                               'padding':'7px 7px'}
                       )
            )

# SEARCH BOX
context.add(
            CssContext('search',
                       tag='div.cx-search-bar',
                       template='medplate/search-box.css_t'
                       )
            )


# Message List
context.add(
            CssContext('messagelist',
                       tag='ul.messagelist li',
                       data = {
                               'margin':'0 0 3px',
                               'padding':'4px 5px 4px 25px'}
                       )
            )

# Message List
context.add(
            CssContext('errorlist',
                       tag='ul.messagelist li.error',
                       data = {
                               'background':'#FFBFBF',
                               'color':'#AF4C4C'}
                       )
            )
