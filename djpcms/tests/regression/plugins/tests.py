from django.contrib.contenttypes.models import ContentType

from djpcms import test
from djpcms.plugins.apps import registered_models, app_model_from_ct, SearchBox

from models import SearchModel


class PluginTools(test.TestCase):
    appurls  = 'regression.plugins.appurls'
    
    def testRegisteredModels(self):
        r = list(registered_models())
        self.assertEqual(len(r),1)
        app,exist = app_model_from_ct(r[0])
        self.assertTrue(exist)
        self.assertEqual(app.model,SearchModel)
        


class SearchBoxPlugin(test.PluginTest):
    appurls  = 'regression.plugins.appurls'
    plugin = SearchBox
    
    def get_plugindata(self, soup_form):
        '''To be implemented by derived classes'''
        ct = ContentType.objects.get_for_model(SearchModel)
        data = super(SearchBoxPlugin,self).get_plugindata(soup_form)
        data['for_model'] = ct.id
        return data
        