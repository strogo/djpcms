from djpcms.contrib.medplate.css import CssContext
from djpcms.contrib.medplate import elements

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
    'text_align': 'left'
    }
   
    
base_context = CssContext('body',
                          tag = 'body',
                          data = defaults,
                          template = 'medplate/base.css_t',
                          ineritable_tag = False)
context = base_context


#________________________________________ ANCHOR
context.add(
            CssContext('anchor',
                       tag = 'a',
                       template = 'medplate/anchor.css_t',
                       data = {
                               'decoration': 'none',
                               'weight':'normal',
                               'color':'#33789C',
                               'background': 'transparent',
                               'color_hover':'#204C64',
                               'background_hover':None
                               }
                       )
            )


#________________________________________ BREADCRUMBS
context.add(
            CssContext('breadcrumbs',
                       tag = 'div.breadcrumbs',
                       template = 'medplate/breadcrumbs.css_t',
                       data = {
                               'font_size': '130%',
                               'padding': '10px 0'}
                       )
            )
                    

#___________________________________ MAIN NAVIGATION
context.add(
            CssContext('nav',
                       tag='ul.main-nav',
                       template='medplate/horizontal_navigation.css_t',
                       process = elements.horizontal_navigation,
                       data = {
                               'anchor_horizontal_padding': 20,
                               'secondary_anchor_width': 100,
                               'secondary_border_with': 1,
                               'hover_background':'transparent',
                               'height': '2.5em',
                               'inner_height': '2.5em',
                               'list_margin': '0',
                               'secondary_radius':0}
                       )
            )


#________________________________________ PAGINATION
context.add(
            CssContext('paginator',
                       tag = 'div.jquery-pagination',
                       template = 'medplate/pagination.css_t',
                       data = {
                               'navigator_float':'left',
                               'information_float':'right',
                               'margin':'0 0 10px 0'
                               }
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

context.add(
            CssContext('table',
                       template='medplate/table.css_t',
                       tag='table.plain',
                       data = {'margin':'10px 0 15px',
                               'cell_padding': '3px 15px 3px 0',
                               'header_font_weight': 'bold',
                               'first_column_font_weight':'bold'}
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
                               'background':'#FFFFE5',
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
