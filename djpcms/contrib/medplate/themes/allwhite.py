from djpcms.contrib.medplate.defaults import base_context

context = base_context.copy()

context.update({ 
    'color': '#333',
    'edit_background': '#f5f5f5'})


context.tags.update({
                     'tag_color':'rgba(51,120,156,0.7)',
                     'tag_hover_color':'rgb(51,120,156)'})