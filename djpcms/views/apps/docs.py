import datetime

from django import http
from django.conf.urls.defaults import url

from djpcms.utils import mark_safe, json 
from djpcms.template import loader
from djpcms.utils.unipath import FSPath as Path
from djpcms.views.appsite import ApplicationBase
from djpcms.views.appview import AppViewBase
from djpcms.views.regex import RegExUrl

    
class DocView(AppViewBase):
    editurl          = None
    
    def __init__(self, regex = '(?P<url>[\w./-]*)', lang = False,
                 version = False, in_navigation = True, **kwargs):
        super(DocView,self).__init__(regex = regex, in_navigation = in_navigation, **kwargs)
        self.lang    = lang
        self.version = version
    
    def old_get_url(self, djp, **urlargs):
        lang = urlargs.get('lang','')
        vers = urlargs.get('version','')
        urls = urlargs.get('url','')
        url  = self.appmodel.baseurl
        if lang:
            url = '%s/%s/' % (url,lang)
        if vers:
            url = '%s/%s/' % (url,vers)
        if urls:
            url = '%s/%s/' % (url,urls.strip('/'))
        return url

    def render(self, djp):
        app     = self.appmodel
        request = djp.request
        args    = djp.urlargs
        page    = djp.page
        lang    = args.get('lang',app.deflang)
        version = args.get('version',app.defversion)
        url     = args.get('url','')
        docroot = self.appmodel.get_docroot(lang, version)
    
        # First look for <bits>/index.fpickle, then for <bits>.fpickle
        bits = url.strip('/').split('/') + ['index.fjson']
        doc = docroot.child(*bits)
        if not doc.exists():
            bits = bits[:-2] + ['%s.fjson' % bits[-2]]
            doc = docroot.child(*bits)
            if not doc.exists():
                raise http.Http404("'%s' does not exist" % doc)

        bits[-1] = bits[-1].replace('.fjson', '')
        name  = self.appmodel.name
        namet = '-'.join([b for b in bits if b])
        template_names = [
                          'docs/%s.html' % namet,
                          'djpcms/docs/%s.html' % namet,
                          'docs/doc.html',
                          ]
        c = {'doc':     json.load(open(doc, 'rb')),
             'env':     json.load(open(docroot.child('globalcontext.json'), 'rb')),
             'lang':    lang,
             'version': version,
             'docurl':  url,
             'update_date': datetime.datetime.fromtimestamp(docroot.child('last_build').mtime()),
             #'home': urlresolvers.reverse('document-index', kwargs={'lang':lang, 'version':version}),
             #'search': urlresolvers.reverse('document-search', kwargs={'lang':lang, 'version':version}),
             'redirect_from': request.GET.get('from', None)}
        
        return loader.render_to_string(template_names, c)
        

class DocApplication(ApplicationBase):
    deflang          = 'en'
    defversion       = 'dev'
    DOCS_PICKLE_ROOT = None
    
    index = DocView(regex = '')
    document = DocView()
    
    def __init__(self, baseurl, application_site, editavailable):
        super(DocApplication,self).__init__(baseurl, application_site, False)
    
    def get_path_args(self, lang, version):
        return (lang, version, "_build", "json")
    
    def get_docroot(self, lang, version):
        docroot = Path(self.DOCS_PICKLE_ROOT).child(*self.get_path_args(lang, version))
        if not docroot.exists():
            raise http.Http404()
        return docroot 
    
    def bodybits(self):
        if self.editurl:
            return mark_safe(u'class="edit documentation"')
        else:
            return mark_safe(u'class="documentation"')
        
    def doc_index_url(self, request, lang, version):
        return '%s%s/%s/' % (self.baseurl,lang,version)
    
    def table_of_content_url(self, request, lang, version):
        return '%s%s/' % (self.doc_index(),'contents')
    
    class Media:
        css = {
            'all': ('djpcms/sphinx/smooth.css',)
        }
    
    
    
    
    
class __OldDocApplication(ApplicationBase):
        
    def old__init__(self, baseurl, application_site, editavailable):
        '''Create a tuple of urls'''
        super(DocApplication,self).__init__(baseurl, application_site, editavailable)
        urls = ()
        appview                 = DocView(self)
        self.root_application   = appview
        self.language = None
        self.version  = None
        #self.urls = (url(r'^$', self.root_application),
        #             url(r'^(?P<lang>[a-z-]+)/$', self.language),
        #             url(r'^(?P<lang>[a-z-]+)/(?P<version>[\w.-]+)/$',
        #                 self.document, {'url': ''},  name = '%s_index' % self.name),
        #             url(r'^(?P<lang>[a-z-]+)/(?P<version>[\w.-]+)/(?P<url>[\w./-]*)/$',
        #                 self.document, name = '%s_details' % self.name),
        #            )
        if self.deflang:
            appview  = DocView(self,appview,lang=True)
            self.language = appview
            urls = url(r'^(?P<lang>[a-z-]+)/$',
                       self.language,
                       {'url': ''},
                       name = '%s_lang' % self.name),
        if self.defversion:
            appview = DocView(self,appview,version=True)
            self.version = appview
            urls += url(r'^(?P<lang>[a-z-]+)/(?P<version>[\w.-]+)/$',
                         self.version,
                         {'url': ''},
                         name = '%s_version' % self.name),
        purl = ''
        if urls:
            urls = (url(r'^$', self.root_application),) + urls
            if self.language:
                purl = '(?P<lang>[a-z-]+)/'
            if self.version:
                purl += '(?P<version>[\w.-]+)/'
        urls += url(r'^%s(?P<url>[\w./-]*)/$' % purl,
                    appview,
                    name = '%s_details' % self.name),
        self.urls = urls
            
    
    def get_root_code(self):
        return self.name
    
    def get_path_args(self, lang, version):
        return (lang, version, "_build", "json")
    
    def get_docroot(self, lang, version):
        docroot = Path(self.DOCS_PICKLE_ROOT).child(*self.get_path_args(lang, version))
        if not docroot.exists():
            raise http.Http404()
        return docroot 

    def get_template(self,page):
        '''
        given a page objects (which may be None)
        return the template file for the get view
        '''
        return None
        
    def bodybits(self):
        if self.editurl:
            return mark_safe(u'class="edit documentation"')
        else:
            return mark_safe(u'class="documentation"')
        
    def doc_index_url(self, request, lang, version):
        return '%s%s/%s/' % (self.baseurl,lang,version)
    
    def table_of_content_url(self, request, lang, version):
        return '%s%s/' % (self.doc_index(),'contents')
    