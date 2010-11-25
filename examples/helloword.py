from djpcms.views.decorator import getview

@getview
def simpleapp():
    return 'Hello World'

