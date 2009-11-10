from tools import BaseUser, nice_name
    
class view(BaseUser):
        
    def title(self):
        fn = nice_name(self.object)
        return "%s's account" % fn
    
    