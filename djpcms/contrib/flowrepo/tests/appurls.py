from djpcms.views import appsite, appview
from djpcms.contrib.flowrepo import cms
from djpcms.contrib.flowrepo.models import FlowItem

class FlowItemApplication(cms.FlowItemApplication):
    inherit = True
    content_names = {cms.Report:'weblog'}

appurls = FlowItemApplication('/', FlowItem),