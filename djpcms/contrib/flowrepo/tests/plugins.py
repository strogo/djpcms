from djpcms.test import TestCase
from djpcms.test import PluginTest
from djpcms.contrib.flowrepo.models import FlowItem
from djpcms.contrib.flowrepo.cms import plugins 


__all__ = ['testFlowItemSelection']


class FlowPlugin(PluginTest):
    
    appurls = 'djpcms.contrib.flowrepo.tests.appurls'
    
    def setUp(self):
        super(FlowPlugin,self).setUp()
        self.clear(True)
        self.makepage('main',FlowItem)
        
        
        
class testFlowItemSelection(FlowPlugin):
    plugin = plugins.FlowItemSelection
    