import json
import datetime

from django import http
from django.shortcuts import render_to_response
from django.template import loader, RequestContext
from django.utils.safestring import mark_safe
from django.conf.urls.defaults import url

from djpcms.utils.unipath import FSPath as Path
from djpcms.views.baseview import djpcmsview
from djpcms.views.appsite import ApplicationBase
from djpcms.views.appview import AppViewBase
from djpcms.views.regex import RegExUrl


class DocView(AppViewBase):
    editurl          = None
    
    def __init__(self, app, parent = None):
        AppViewBase.__init__(self, parent = parent)
        self.appmodel = app
        
class Index(DocView):
    
    def __init__(self, app):
        super(Index,self).__init__(app)
    
    def __call__(self, request, *args, **kwargs):
        a = self.appmodel
        return http.HttpResponseRedirect('%s%s/%s/' % (a.baseurl,a.deflang,a.defversion))
    
    def isroot(self):
        return True

class Language(DocView):
    
    def __init__(self, app, parent):
        super(Language,self).__init__(app,parent)
    
    def __call__(self, request, lang, *args, **kwargs):
        a = self.appmodel
        return http.HttpResponseRedirect('%s%s/%s/' % (a.baseurl,lang,a.defversion))

class Document(DocView):
    
    def __init__(self, app, parent):
        super(Document,self).__init__(app,parent)
    
    def handle_response(self, djp):
        request = djp.request
        args    = djp.urlargs
        page    = djp.page
        lang    = args.get('lang')
        version = args.get('version')
        url     = args.get('url')
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
                          '%s/docs/%s.html' % (name,namet),
                          '%s/docs/doc.html' % name,
                          'docs/%s.html' % namet, 
                          'docs/doc.html'
                          ]
        c = {
             'djp':     djp,
             'doc':     json.load(open(doc, 'rb')),
             'env':     json.load(open(docroot.child('globalcontext.json'), 'rb')),
             'lang':    lang,
             'version': version,
             'docurl':  url,
             'update_date': datetime.datetime.fromtimestamp(docroot.child('last_build').mtime()),
             #'home': urlresolvers.reverse('document-index', kwargs={'lang':lang, 'version':version}),
             #'search': urlresolvers.reverse('document-search', kwargs={'lang':lang, 'version':version}),
             'redirect_from': request.GET.get('from', None),
             'grid':          self.grid960(page)
             }
        
        return render_to_response(template_names,
                                  RequestContext(request,c))
        


class DocApplication(ApplicationBase):
    deflang          = 'en'
    defversion       = 'dev'
    DOCS_PICKLE_ROOT = None
    
    def __init__(self, baseurl, application_site, editavailable):
        '''
        Create a tuple of urls
        '''
        super(DocApplication,self).__init__(baseurl, application_site, editavailable)       
        self.root_application   = Index(self)
        self.language           = Language(self,self.root_application)
        self.document           = Document(self,self.language)
        self.urls = (url(r'^$', self.root_application),
                     url(r'^(?P<lang>[a-z-]+)/$', self.language),
                     url(r'^(?P<lang>[a-z-]+)/(?P<version>[\w.-]+)/$',
                         self.document, {'url': ''},  name = '%s_index' % self.name),
                     url(r'^(?P<lang>[a-z-]+)/(?P<version>[\w.-]+)/(?P<url>[\w./-]*)/$',
                         self.document, name = '%s_details' % self.name),
                    )
    
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
    