from djpcms.views import Factory


class BaseUser(Factory.childview):
    
    def incache(self):
        return False


def nice_name(user):
    fn = user.first_name
    if not fn:
        return user.username
    else:
        return fn