from djpcms.contrib.medplate.themes.allwhite import context as base_context

context = base_context.copy()


context.update({'font_size': '13px',
                'line_height': '17px',
                'font_family': "'Lucida Grande',Arial,sans-serif"})

context.nav.update({'display':'block',
                    'font_weight': 'bold',
                    'color': '#E7E5E5',
                    'background':'#666',
                    'hover_background':'#ccc',
                    'selected_background':'#dcdcdc',
                    'hover_color': '#444',
                    'selected_color':'#444',
                    'padding': '5px 0',     # Padding for outer ul
                    'height': '30px',
                    'inner_radius': '10px',
                    'secondary_width': '100px',
                    'list_margin': '0 5px',
                    'anchor_padding': '0 20px',
                    'radius': '14px'})

context.breadcrumbs.update({'font_size': '120%',
                            'font_weight': 'bold',
                            'padding': '15px 0',
                            'text_align':'center'})


# Style box
context.box.update({'background':'#ccc',
                    'radius':'7px'})
context.box.bd.update({'background':'#fff',
                       'radius_top_right':'0px',
                       'radius_top_left':'0px'})
context.box.ft.update({'background':'#fff',
                       'radius_top_right':'0px',
                       'radius_top_left':'0px'})
context.box.hd.update({'background':'#ccc'})