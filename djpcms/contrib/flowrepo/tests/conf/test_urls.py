from djpcms.views import appsite, appview

from flowrepo import cms


class FlowItemApplication(cms.FlowItemApplication):
    inherit = True
    content_names = {cms.Report:'weblog'}

appsite.site.register('/', cms.FlowItemApplication, model = cms.FlowItem)


