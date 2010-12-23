

def test_styling_function(request):
    if request.user.is_authenticated():
        return {'all':['djpcms/authenticated.css']}
    else:
        return {'all':['djpcms/unknown.css']}