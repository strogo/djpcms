# Classes for AJAX - Django interaction

from jsonbase import jsonbase


class ajaxhtml(jsonbase):
    
    def __init__(self):
        self.floatright     = 'float-right'
        self.plainlist      = 'plainlist'
        
        d = {}
        self.__dict = d
        prefix                       = 'prospero_'
        target                       = '_target'
        d['GRID_WIDGET_CLASS']       = 'grid-widget'
        d['grid_widget_inner']       = 'safe-padding'
        d['gwrap']                   = 'g-wrap'
        d['wwrap']                   = 'w-wrap'
        d['FEEDS_HTML_CLASS']        = 'dynamic-feeds'
        d['accordion']               = 'accordion-element'        
        d['target']                  = target
        d['body_class']              = 'yui-skin-sam'
        d['calendar_class']          = 'calendar-input'
        d['currency_input']          = 'currency-input'
        
        # components
        d['title_page']              = 'title-page'
        d['module_class']            = 'flowpanel'
        d['ts_plot']                 = 'ts-plot-module'
        d['portfolio_form']          = 'portfolio-form'
        d['portfolio']               = 'portfolio-holder'
        
        #
        # Search classes
        d['search_entry']            = 'search-entry'
        d['search_count']            = 'search-count'
        d['search_result']           = 'search-result'
        d['search_item']             = 'search-result-item'
        #
        # AJAX classes
        d['post_view_key']           = 'xhr'
        d['ajax']                    = 'ajax'
        d['select_menu']             = 'ajax-select-menu'
        d['ajax_autocomplete']       = 'ajax-autocomplete'
        
        # Not sure about those 
        d['edit_inline']             = 'edit-inline-form'
        d['edit_link']               = 'edit-link'
        d['edit_inline_target']      = d['edit_inline'] + target
        d['formlet_wrapper']         = '%sformlet' % prefix
        d['ajax_table']              = 'tablesorter'
        
        #
        d['errorlist']               = 'errorlist'
        d['formmessages']            = 'form-messages'
        d['formerrors']              = 'global-form-errors'
        d['ajax_server_error']       = 'ajax-server-error'
        
        d['ajax_form_data']          = 'ajax-input-form-data'
        d['ajax_output_form_data']   = 'ajax-output-form-data'
        d['ajax_edit_link']          = 'ajax-edit-link'     
        d['ajax_tab_link']           = 'ajax-tab-link'
        d['date_format']             = 'D d M yy'
        
        #
        # css decorators
        d['edit']                    = 'editable'
        d['delete']                  = 'deletable'
        d['secondary_in_list']       = 'secondary'
        d['link_selected']           = 'selected'
        d['align_forms']             = 'aligned'
        d['menu_item']               = 'menuitem'
        
        #
        # site-content management
        d['site_content_prefix']     = 'djpcontent'
        d['content_simple']          = 'djp-simple'
        
        for k,v in d.iteritems():
            object.__setattr__(self,k,v)
        
    def dict(self):
        return self.__dict
    


classes = ajaxhtml()