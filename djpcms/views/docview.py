import json
import datetime

from django.conf import settings
from django import http
from django.shortcuts import render_to_response
from django.template import loader, RequestContext
from django.utils.safestring import mark_safe

from unipath import FSPath as Path

from djpcms.views.baseview import djpcmsview



class DocView(djpcmsview):
    # Name the documents
    name             = None
    baseurl          = '/'
    deflang          = 'en'
    DOCS_PICKLE_ROOT = None
    editurl          = None
    
    def make_urls(self):
        from django.conf.urls.defaults import url
        self.doc_index = '%s_doc_index' % self.name
        b = self.baseurl[1:]
        return (url(r'^%s$' % b, self.index),
                url(r'^%s(?P<lang>[a-z-]+)/$' % b, self.language),
                url(r'^%s(?P<lang>[a-z-]+)/(?P<version>[\w.-]+)/$' % b,
                    self.document,
                    {'url': ''},
                    name = '%s_doc_index' % self.name),
                url(r'^%s(?P<lang>[a-z-]+)/(?P<version>[\w.-]+)/(?P<url>[\w./-]*)/$' % b,
                    self.document,
                    name = '%s_doc_details' % self.name),
                )
    urls = property(fget = make_urls)
    
    def get_path_args(self, lang, version):
        return (lang, version, "_build", "json")
    
    def get_docroot(self, lang, version):
        docroot = Path(self.DOCS_PICKLE_ROOT).child(*self.get_path_args(lang, version))
        if not docroot.exists():
            raise Http404()
        return docroot 
    
    def index(self, request):
        return http.HttpResponseRedirect('%s%s/dev/' % (self.baseurl,self.deflang))
    
    def language(self, request, lang):
        return http.HttpResponseRedirect('%s%s/dev/' % (self.baseurl,lang))

    def get_template(self,page):
        '''
        given a page objects (which may be None)
        return the template file for the get view
        '''
        return None
            
    def document(self, request, lang, version, url = None):
        djp = self.requestview(request, lang = lang, version = version, url = url)
        return djp.response()
    
    def render(self, djp):
        request = djp.request
        args    = djp.urlargs
        lang    = args.get('lang')
        version = args.get('version')
        url     = args.get('url')
        docroot = self.get_docroot(lang, version)
    
        # First look for <bits>/index.fpickle, then for <bits>.fpickle
        bits = url.strip('/').split('/') + ['index.fjson']
        doc = docroot.child(*bits)
        if not doc.exists():
            bits = bits[:-2] + ['%s.fjson' % bits[-2]]
            doc = docroot.child(*bits)
            if not doc.exists():
                raise Http404("'%s' does not exist" % doc)

        bits[-1] = bits[-1].replace('.fjson', '')
        namet = '-'.join([b for b in bits if b])
        template_names = [
                          '%s/docs/%s.html' % (self.name,namet),
                          '%s/docs/doc.html' % self.name,
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
             'grid':          self.grid960()
             }
        
        return render_to_response(template_names,
                                  RequestContext(request,c))
        
    def bodybits(self):
        if self.editurl:
            return mark_safe(u'class="edit documentation"')
        else:
            return mark_safe(u'class="documentation"')
        
    def doc_index_url(self, request, lang, version):
        return '%s%s/%s/' % (self.baseurl,lang,version)
    
    def table_of_content_url(self, request, lang, version):
        return '%s%s/' % (self.doc_index(),'contents')
    