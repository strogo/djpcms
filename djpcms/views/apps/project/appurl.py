#
# djpcms application for django-flowrepo project application
#
#@requires: django-flowrepo
#@see: yet to be released. Do not used it in production
#
from djpcms.views.apps.flowrepo.appurl import FlowModelApplication


class ProjectApplication(FlowModelApplication):
    inherit  = True