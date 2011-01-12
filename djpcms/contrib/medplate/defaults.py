from djpcms.contrib.medplate.css import CssContext
from djpcms.contrib.medplate import elements

defaults = { 
    'background': '#fff',
    'color': '#000',
    #
    #
    'font_family': "Helvetica,Arial,'Liberation Sans',FreeSans,sans-serif",
    'font_size': '14px',
    'font_weight': 'normal',
    'font_style': 'normal',
    'line_height': '1.3em',
    'text_align': 'left',
    #
    'block_spacing': '10px'
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
                               'background': 'transparent',
                               'font_size': '130%',
                               'padding': '10px 0'}
                       )
            )
                    
#________________________________________ MAIN NAVIGATION
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


#________________________________________ UNIFORM
context.add(
            CssContext('uniform',
                       tag = 'form.uniForm',
                       template = 'medplate/uniform.css_t',
                       data = {
                               'background':'transparent',
                               'input_border':'1px solid #ccc',
                               'input_padding': '3px 0',
                               'table_padding': '2px 5px 2px 0'
                               }
                       )
            )


#________________________________________ SUBMITS AND BUTTONS
context.add(
            CssContext('submit',
                       tag = 'input[type="submit"]',
                       template = 'medplate/submit.css_t',
                       data = {
                               'background':'#FFFFFF',
                               'border':'1px solid #aaa',
                               'text_align':'center',
                               'padding': '3px 5px',
                               'min_width': '50px'
                               }
                       )
            )

#________________________________________ TAGS
context.add(
            CssContext('tags',
                       tag='div.tagindex',
                       template='medplate/tags.css_t',
                       data = {
                               'background': 'transparent',
                               'text_align': 'justify',
                               'tag_opacity': 0.7}
                       )
            )


#________________________________________ OBJECT DEFINITIONS
context.add(
            CssContext('object_definitions',
                       tag='div.object-definition',
                       template='medplate/object-definition.css_t',
                       data = {
                               'background': 'transparent'
                               }
                       )
            )


#________________________________________ BOX
context.add(
            CssContext('box',
                       tag='div.djpcms-html-box',
                       template='medplate/box/box.css_t',
                       data = {'padding':'2px'},
                       elems = [CssContext('hd',
                                           tag='div.hd',
                                           template='medplate/box/header.css_t',
                                           data={'background':'transparent',
                                                 'padding':'6px 12px',
                                                 'text_transform':'uppercase',
                                                 'title_size':'110%',
                                                 'font_weight':'normal',
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


#________________________________________ EDITING
context.add(
            CssContext('editing',
                       tag = 'body.edit',
                       template='medplate/editing.css_t',
                       data = {
                               'background': '#f5f5f5',
                               'color': '#000',
                               'placeholder_border': '2px dashed #666'
                               }
                       )
            )

context.add(
            CssContext('element',
                       tag='div.flat-element',
                       data = {'overflow':'hidden',
                               'padding':0}
                       )
            )


#________________________________________ PANEL
context.add(
            CssContext('panel',
                       tag='div.flat-panel',
                       data = {'overflow':'hidden',
                               'margin':0,
                               'padding':'7px 7px'}
                       )
            )


#________________________________________ FLAT BOX
context.add(
            CssContext('flatbox',
                       tag='div.flat-box',
                       template='medplate/box/box.css_t',
                       data = {'overflow':'hidden',
                               'margin':0,
                               'padding':0},
                       elems = [CssContext('hd',
                                           tag='div.hd',
                                           template='medplate/box/header.css_t',
                                           data={'background':'transparent',
                                                 'font_weight': 'bold',
                                                 'title_size':'110%',
                                                 'padding':'5px 5px',
                                                 'overflow':'hidden'}),
                                CssContext('bd',
                                           tag='div.bd',
                                           data={'background':'transparent',
                                                 'padding':0})
                                ]
                       )
            )


#________________________________________ PLAIN TABLE
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

#________________________________________ SEARCH BOX
context.add(
            CssContext('search',
                       tag='div.cx-search-bar',
                       template='medplate/search-box.css_t'
                       )
            )


#________________________________________ JQUERY UI-TABS
context.add(
            CssContext('tabs',
                       tag='.ui-tabs',
                       template='medplate/tabs.css_t'
                       )
            )


#________________________________________ MESSAGE LIST & ERROR LIST
context.add(
            CssContext('messagelist',
                       tag='ul.messagelist li',
                       data = {
                               'background':'#FFFFE5',
                               'color':'#666',
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
