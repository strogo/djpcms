from djpcms.contrib.medplate.themes.allwhite import context as base_context

context = base_context.copy()

border_color = '#e0e0e0'

context.update({'font_size': '13px',
                'line_height': '18px',
                'font_family': "'Lucida Grande',Arial,sans-serif",
                'block_spacing': '15px'})

context.anchor.update({'color':'#36566B',
                       'color_hover':'#e17009',
                       'font_weight':'bold'})

context.nav.update({'display':'block',
                    'main_text_shadow': '0 2px 2px rgba(0, 0, 0, 0.5)',
                    'secondary_text_shadow': 'none',
                    # SHADOW OF DROP DOWN MENU
                    'secondary_border_color':'#b4b4b4',
                    'drop_down_shadow': '10px 10px 5px rgba(0,0,0, .5)',
                    'font_weight': 'bold',
                    'color': '#E7E5E5',
                    'background':'#666',
                    'hover_background':'#ccc',
                    'secondary_hover_background':'#c2c2c2',
                    'selected_background':'#dcdcdc',
                    'hover_color': '#444',
                    'selected_color':'#444',
                    'padding': '2px 0',     # Padding for outer ul
                    'height': '30px',
                    'inner_radius': '10px',
                    'list_margin': '0 5px',
                    'anchor_padding': '0 20px',
                    'radius': '14px'})

context.breadcrumbs.update({'font_size': '120%',
                            'font_weight': 'bold',
                            'padding': '15px 0',
                            'text_align':'center'})

context.panel.update({'background':'#fafafa',
                      'border':'2px solid {0}'.format(border_color)})

# Style box
boxcolor = 'rgba(143,172,191,1)'
context.box.update({'background':boxcolor,
                    'radius':'7px'})
context.box.bd.update({'background':'#fff',
                       'radius_top_right':'0px',
                       'radius_top_left':'0px'})
context.box.ft.update({'background':'#fff',
                       'radius_top_right':'0px',
                       'radius_top_left':'0px'})
context.box.hd.update({'background':boxcolor,
                       'text_shadow':'1px 1px 3px #fff'})

#tablesorter
context.tablesorter.update({
                            'font_size': '11px',
                            'head_border': '1px solid #fff',
                            'head_background':boxcolor,
                            })

# Uniforms
context.uniform.update({'input_border':'2px solid #dfdfdf'})

# Submits
context.submit.update({'background':'url("{0}djpcms/img/nav-bg.gif") repeat-x scroll center bottom #fff'.format(context.mediaurl),
                       'color': '#666',
                       'hover_border': '2px solid #aaa'})

