from djpcms.views import appsite, appview
from djpcms.contrib.flowrepo import cms
from djpcms.contrib.flowrepo.models import FlowItem, WebAccount


appurls = (
           cms.WebAccountApplication('/webacc/', WebAccount),
           cms.FlowItemApplication('/', FlowItem, content_names = {cms.Report:'weblog'})
           )