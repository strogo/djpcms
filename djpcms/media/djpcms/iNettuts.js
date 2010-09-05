
(function($) {
	
	var iDJP = {
		    		    
		    settings : {
		        columns : '.djpcms-block',
		        widgetSelector: '.edit-block',
		        handleSelector: '.hd',
		        contentSelector: '.widget-content',
		        widgetDefault : {
		            movable: true,
		            removable: true,
		            collapsible: true,
		            editable: true,
		            colorClasses : ['color-yellow', 'color-red', 'color-blue', 'color-white', 'color-orange', 'color-green']
		        },
		        widgetIndividual : {
		            intro : {
		                movable: false,
		                removable: false,
		                collapsible: false,
		                editable: false
		            },
		            gallery : {
		                colorClasses : ['color-yellow', 'color-red', 'color-white']
		            }
		        }
		    },

		    init : function () {
		        this.makeSortable();
		    },
		    
		    getWidgetSettings : function (id) {
		        var settings = this.settings;
		        return (id&&settings.widgetIndividual[id]) ? $.extend({},settings.widgetDefault,settings.widgetIndividual[id]) : settings.widgetDefault;
		    },
		    
		    makeSortable : function () {
		        var iNettuts = this, settings = this.settings;
		        function sitems() {
	                var notSortable = '';
	                $(settings.widgetSelector,$(settings.columns)).each(function (i) {
	                    if (!iNettuts.getWidgetSettings(this.id).movable) {
	                        if(!this.id) {
	                            this.id = 'widget-no-id-' + i;
	                        }
	                        notSortable += '#' + this.id + ',';
	                    }
	                });
	                return $('> li:not(' + notSortable + ')', settings.columns);
	            }
		        
		        var $sortableItems = sitems(); 
		        $sortableItems.find(settings.handleSelector).css({
		            cursor: 'move'
		        }).mousedown(function (e) {
		            $sortableItems.css({width:''});
		            $(this).parent().css({
		                width: $(this).parent().width() + 'px'
		            });
		        }).mouseup(function () {
		            if(!$(this).parent().hasClass('dragging')) {
		                $(this).parent().css({width:''});
		            } else {
		                $(settings.columns).sortable('disable');
		            }
		        });

		        $(settings.columns).sortable({
		            items: $sortableItems,
		            connectWith: $(settings.columns),
		            handle: settings.handleSelector,
		            placeholder: 'widget-placeholder',
		            forcePlaceholderSize: true,
		            revert: 300,
		            delay: 100,
		            opacity: 0.8,
		            containment: 'document',
		            start: function (e,ui) {
		                $(ui.helper).addClass('dragging');
		            },
		            stop: function (e,ui) {
		                $(ui.item).css({width:''}).removeClass('dragging');
		                $(settings.columns).sortable('enable');
		            }
		        });
		    }
		  
		};


iDJP.init();

})(jQuery);

