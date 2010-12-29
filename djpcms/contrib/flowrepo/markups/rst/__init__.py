import os
import time
from docutils.core import publish_parts

from sphinx.application import Sphinx

import djpcms
from djpcms.utils import gen_unique_id
from djpcms.contrib.flowrepo.markups import application
from .builders import SingleStringHTMLBuilder

def info(self, *args,**kwargs):
    pass

Sphinx.info = info

class Application(object):
    code = 'rst'
    name = 'reStructuredText'
    
    def setup(self):
        settings = djpcms.get_site().settings
        cfgdir = settings.SITE_DIRECTORY
        srcdir = os.path.join(settings.SITE_DIRECTORY,'flowtmp')
        outdir = os.path.join(settings.MEDIA_ROOT,'site')
        if not os.path.exists(outdir):
            os.mkdir(outdir)
        if not os.path.exists(srcdir):
            os.mkdir(srcdir)
        self.srcdir = srcdir
        self.cfgdir = cfgdir
        self.outdir = outdir
        self.media_url = '{0}site/'.format(settings.MEDIA_URL)
        
    def __call__(self, text):
        sx = Sphinx(self.srcdir,
                    self.cfgdir,
                    self.outdir,
                    self.srcdir,SingleStringHTMLBuilder.name)
        sx.media_url = self.media_url
        master_doc = gen_unique_id()
        mc = (master_doc,'env')
        sx.config.values['master_doc'] = mc
        sx.config.config_values['master_doc'] = mc
        fname = os.path.join(self.srcdir,'{0}.rst'.format(master_doc))
        fdoc = os.path.join(self.srcdir,'{0}.doctree'.format(master_doc))
        f = open(fname,'w')
        f.write(text)
        f.close()
        sx.build(force_all=True)
        res = sx.builder.docwriter.parts['fragment']
        os.remove(fname)
        os.remove(fdoc)
        return res
    
    
app = Application()