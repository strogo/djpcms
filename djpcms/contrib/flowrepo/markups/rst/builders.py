from docutils.core import publish_parts
from docutils.io import StringOutput

from sphinx.builders import BUILTIN_BUILDERS
from sphinx.builders.html import SingleFileHTMLBuilder
from sphinx.writers.html import HTMLWriter
from sphinx.util.osutil import relative_uri
    

class SingleStringHTMLBuilder(SingleFileHTMLBuilder):
    name = 'singlestringhtml'
    
    def info(self, *args, **kwargs):
        '''Silence the logger'''
        pass
    
    def write_doc(self, docname, doctree):
        destination = StringOutput(encoding='utf-8')
        doctree.settings = self.docsettings

        self.secnumbers = self.env.toc_secnumbers.get(docname, {})
        media_url = self.app.media_url
        self.imgpath = '{0}_images'.format(media_url)
        self.post_process_images(doctree)
        self.dlpath = relative_uri(self.get_target_uri(docname), '_downloads')
        self.docwriter.write(doctree, destination)
        self.docwriter.assemble_parts()
        
    def finish(self):
        self.copy_image_files()
        self.copy_download_files()
        #self.copy_static_files()
        #self.write_buildinfo()
        #self.dump_inventory()
        
    
    
BUILTIN_BUILDERS.update({'singlestringhtml':  SingleStringHTMLBuilder})