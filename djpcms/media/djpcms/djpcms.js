/*
 * File:         djpcms.js
 * Description:  djpcms Javascript Site Manager
 * Author:       Luca Sbardella
 * Language:     Javascript
 * License:      new BSD licence
 * Contact:      luca.sbardella@gmail.com
 * @requires:	 jQuery
 * 
 * Copyright (c) 2009, Luca Sbardella
 * New BSD License 
 * http://www.opensource.org/licenses/bsd-license.php
 *
 * 
 */


/**
 * 
 * djpcms site handle
 * 
 * @param _media_url_base,	String base url for media files
 * @param options_, Object page-specific options
 */
(function($) {
	$.extend({
		djpcms: new function() { 
		
			var decorators = {};
			var jsonCallBacks = {};
	
			this.options = {
				media_url:		   "/media-site/",
				autoload_class:	   "autoload",
				ajax_server_error: "ajax-server-error",
				errorlist:		   "errorlist",
				formmessages:	   "form-messages",
				date_format: 	   "d M yy",
				bitly_key:		   null,
				twitter_user:	   null,
				fadetime:		   200,
				ajaxtimeout:	   30,
				tablesorter:	   {widgets:['zebra']},
				debug:			   false
			};
			
			this.log = function(s) {
				if(this.options.debug) {
					if (typeof console != "undefined" && typeof console.debug != "undefined") {
						console.log('$.djpcms: '+ s);
					} else {
						//alert(s);
					}
				}
			}
			
			this.postparam = function(name) {
				var reqdata = {submitkey: this.options.post_view_key};
				if(name){
					reqdata[this.options.post_view_key] = name;
				}
				return reqdata;
			};
			
			// Set options
			this.set_options = function(options_) {
				$.extend(true, this.options, options_);
			};
			
			// Add a new decorator
			this.addDecorator = function(deco) {
				decorators[deco.id] = deco;
			};
			// Add a new decorator
			this.addJsonCallBack = function(jcb) {
				jsonCallBacks[jcb.id] = jcb;
			};
			
			// Remove a decorator
			this.removeDecorator = function(rid) {
				var ndecos = {};
				$.each(decorators,function(id,decorator) {
					if(id != rid) {
						ndecos[id] = decorator;
					}
				});
				this.decorators = ndecos;
			};
			
			/**
			 * Handle a JSON call back by looping through all the callback objects registered
			 * @param data JSON object
			 * @param el (Optional) jQuery object or HTMLObject
			 * @return boolean, true if everything is good, false if an error has occured
			 */
			this.jsonCallBack = function(data, status, elem) {
				if(status == "success") {
					var id  = data.header;
					var jcb = jsonCallBacks[id];
					if(jcb) {
						return jcb.handle(data.body, elem) & data.error;
					}
				}
			};
	
			this.construct = function() {
				var this_ = $.djpcms;
				return this.each(function() {
					var config = this_.options;
					
					// store common expression for speed					
					var $this = $(this);
					
					$.each(decorators,function(id,decorator) {
						this_.log('Adding decorator ' + decorator.id);
						decorator.decorate($this,config);
					});
				});
			};
		}
	});
	
	// extend plugin scope
	$.fn.extend({
        djpcms: $.djpcms.construct
	});
	
	
	var dj = $.djpcms;
	
	
	/**
	 * ERROR and SERVER ERROR callback
	 */
	dj.addJsonCallBack({
		id: "error",
		handle: function(data, elem) {
			var el = $('<div title="Something did not work."></div>').html('<p>'+data+'</p>');
			el.dialog({modal:true});
		}
	});
	dj.addJsonCallBack({
		id: "servererror",
		handle: function(data, elem) {
			var el = $('<div title="Unhandled Server Error"></div>').html('<p>'+data+'</p>');
			el.dialog({modal:true});
		}
	});
	
	/**
	 * html JSON callback
	 */
	dj.addJsonCallBack({
		id: "htmls",
		handle: function(data, elem) {
			$.each(data, function(i,b) {
				var el = $(b.identifier,elem);
				if(!el.length & b.alldocument) {
					el = $(b.identifier);
				}
				if(el.length) {
					if(b.type == 'hide') {
						el.hide();
					}
					else if(b.type == 'show') {
						el.show();
					}
					else if(b.type == 'value') {
						el.val(b.html);
					}
					else {
						if(b.type == 'append') {
							el.html(el.html() + b.html);
						}
						else if(b.type == 'replacewith') {
							el.replaceWith(b.html);
						}
						else {
							el.html(b.html);
						}
						el.djpcms();
						el.show();
					}
				}
			});
			return true;
		}
	});
	
	/**
	 * Remove html tags
	 */
	dj.addJsonCallBack({
		id: "remove",
		handle: function(data, elem) {
			$.each(data, function(i,b) {
				var el = $(b.identifier,elem);
				if(!el.length & b.alldocument) {
					el = $(b.identifier);
				}
				if(el) {
					el.fadeOut($.djpcms.options.fadetime,el.remove());
				}
			});
			return true;
		}
	});
	
	/**
	 * Redirect
	 */
	dj.addJsonCallBack({
		id: "redirect",
		handle: function(data, elem) {
			window.location = data;
		}
	});
	
	/**
	 * Dialog callback
	 * 
	 * Create a jQuery dialog from JSON data
	 */
	dj.addJsonCallBack({
		id: "dialog",
		handle: function(data, elem) {
			var el = $('<div></div>').html(data.html);
			var buttons = {};
			$.each(data.buttons,function(n,b) {
				buttons[b.name] = function() {
					b.d = $(this);
					
					b.dialogcallBack = function(data) {
						$.djpcms.jsonCallBack(data,'success',el);
						if(b.close) {
							b.d.dialog("close");
						}
					};
					
					if(b.url) {
						var params = $('form',el).formToArray();
						if(b.func) {
							var extra = $.djpcms.postparam(b.func);
							$.each(extra, function(k,v) {
								params.push({'name':k, 'value':v});
							});
						}
						$.post(b.url,$.param(params),b.dialogcallBack,"json");
					}
					else {
						b.d.dialog('close');
					}
				};
			});
			var options = data.options;
			options.buttons = buttons;
			el.dialog(options);
			return true;
		}
	});
	
	
	////////////////////////////////////////////////////////////////////////////////////////////////
	//						DECORATORS
	////////////////////////////////////////////////////////////////////////////////////////////////
	
	
	/**
	 * Ajax links, buttons and select 
	 */
	dj.addDecorator({
		id:	"ajax_widgets",
		description: "add ajax functionality to links, buttons and selects",
		decorate: function($this,config) {
			var ajaxclass = config.ajaxclass ? config.ajaxclass : 'ajax';
			
			function sendrequest(elem,name) {
				var url = elem.attr('href');
				if(url) {
					var p = $.djpcms.postparam(name);
					$.post(url,$.param(p),$.djpcms.jsonCallBack,"json");
				}
			}
			function deco(event,elem) {
				event.preventDefault();
				var a = $(elem);
				var name = a.attr('name');
				if(name == 'delete') {
					var el = $('<div></div>').html('Please confirm delete.');
					el.dialog({modal: true,
							   draggable: false,
							   resizable: false,
							   buttons: {
								   Ok : function() {
									   $( this ).dialog( "close" );
									   sendrequest(a,name);
								   },
								   Cancel: function() {
									   $(this).dialog( "close" );
								   }
						}});
				}
				else {
					sendrequest(a,name);
				}
			}
			$('a.'+ajaxclass,$this).click(function(event) {deco(event,this);});
			$('button.'+ajaxclass,$this).click(function(event) {deco(event,this);});
			$('select.'+ajaxclass,$this).change(function(event) {
				var a    = $(this);
				var _url = a.attr('href');
				var f    = a.parents('form');
				if(f.length == 1 && !_url) {
					_url = f.attr('action');
				}
				if(!_url) {
					_url = window.location.toString();
				}
				if(!f) {
					var p   = $.djpcms.postparam(a.attr('name'));
					p.value = a.val();
					$.post(_url,$.param(p),$.djpcms.jsonCallBack,"json");
				}
				else {
					var opts = {
							url:       _url,
							type:      'post',
							success:   $.djpcms.jsonCallBack,
							submitkey: config.post_view_key,
							dataType: "json",
							};
					f[0].clk = this;
					f.ajaxSubmit(opts);
				}
			});
			
			var presubmit_form = function(formData, jqForm, opts) {
				jqForm.css({'opacity':'0.5'});
				$('.'+config.errorlist+
				 ',.'+config.ajax_server_error,jqForm).fadeOut(100);
				return true;
			};
			var success_form = function(o,s,jform) {
				$.djpcms.jsonCallBack(o,s,jform);
				jform.css({'opacity':'1'});
			};
			$('form.'+ajaxclass,$this).each(function() {
				var f = $(this);
				var opts = {url:      	 this.action,
					   		type:     	 this.method,
					   		success:  	 success_form,
					   		submitkey: 	 config.post_view_key,
					   		dataType:    "json",
					   		beforeSubmit: presubmit_form};
				f.ajaxForm(opts);
				if(f.hasClass(config.autoload_class))  {
					var name = f.attr("name");
					f[0].clk = $(":submit[name='"+name+"']",f)[0];
					f.ajaxSubmit(opts);
				}
			});
		}
	});
	
	/**
	 * Autocomplete Off
	 */
	dj.addDecorator({
		id:"autocomplete_off",
		decorate: function($this,config) {
			$('.autocomplete-off',$this).each(function() {
				$(this).attr('autocomplete','off');
			});
			$('input:password',$this).each(function() {
				$(this).val('').attr('autocomplete','off');
			});
		}
	});
	
	/**
	 * box decorator
	 * 
	 */
	dj.addDecorator({
		id:"djpcms_box",
		decorate: function($this,config) {
			var cname = '.djpcms-html-box';
			var bname = '.hd';
			$(cname,$this).each(function() {
				var el = $(this);
				if(el.hasClass('collapsable')) {
					var container = $(bname,el);
					if(container.length) {
						var link = $('a.collapse',container);
						if(link.length) {
							link.mousedown(function (e) {
								e.stopPropagation();    
							}).toggle(function() {
								$(this).parents(cname).toggleClass('collapsed');
								return false;
							},function() {
								$(this).parents(cname).toggleClass('collapsed');
								return false;
							});
						}
					}
				}
			});
		}
	});
	
	
	/**
	 * Accordion menu
	 */
	dj.addDecorator({
		id:"accordion_menu",
		decorate: function($this,config) {
			$('ul.accordionmenu',$this).each(function() {
				var menu = $(this);
				var act = $('li.selected a',menu);
				if(!act.length) {
					act = 0;
				}
				var el = menu.accordion({header: "a.menuitem",
										 event: "mouseover",
										 active: act});
				menu.fadeTo(config.fadetime,1);
			});
		}
	});
	
	
	/**
	 * Table-sorter decorator
	 * decorate tables with jquery.tablesorter plugin
	 * Plugin can be found at http://tablesorter.com/
	 */
	dj.addDecorator({
		id:"tablesorter",
		decorate: function($this,config) {
			$('table.tablesorter',$this).each(function() {
				$(this).tablesorter(config.tablesorter);
			});
		}
	});
	
	
	// Calendar Date Picker Decorator
	dj.addDecorator({
		id:"Date_Picker",
		decorate: function($this, config) {
			var ajaxclass = config.calendar_class ? config.calendar_class : 'dateinput';
			$('input.'+ajaxclass,$this).each(function() {
				$(this).datepicker({dateFormat: config.date_format});
			});
		}
	});
	
	/**
	 * jQuery UI Tabs
	 */
	dj.addDecorator({
		id:"ui_tabs",
		decorate: function($this, config) {
			$('.ui-tabs',$this).tabs();
		}
	});
	
	/**
	 * Cycle jQuery Plugin decorator, from django-flowrepo
	 * 
	 */ 
	dj.addDecorator({
		id:"image_cycle",
		decorate: function($this, config) {
			$('.image-cycle', $this).each(function() {
				var this_ = $(this);
				var w     = this_.width();
				var h     = this_.height();
				var classes = this.className.split(" ");
				var type_  = 'fade';
				var speed_ = 5000;
				var timeout_ = 10000;
				$('img',this_).width(w).height(h);
				$.each(classes,function(i,v) {
					if(v.substr(0,6) == "speed-"){
						try {
							speed_ = parseInt(v.substr(6));
						} catch(e) {}
					}
					else if(v.substr(0,8) == "timeout-"){
						try {
							timeout_ = parseInt(v.substr(8));
						} catch(e) {}
					}
					else if(v.substr(0,5) == "type-") {
						type_ = v.substr(5);
					}
                });
				this_.cycle({fx: type_,
						  speed: speed_,
						  timeout: timeout_});
			});
		}
	});
	
	dj.addDecorator({
		id:"color_picker",
		decorate: function($this, config) {
			$('input.color-picker', $this).each(function() {
				var div = $('<div class="color-picker"></div>');
				var iel = $(this).hide().after(div);
				var v = iel.val();
				div.append(iel.remove());
				div.css('backgroundColor', '#' + v);
				div.ColorPicker({
					onSubmit: function(hsb, hex, rgb, el) {
						var elem = $(el);
						$('input',elem).val(hex);
						elem.css('backgroundColor', '#' + hex);
						elem.ColorPickerHide();
					},
					onBeforeShow: function () {
						var v = $('input',this).val();
						$(this).ColorPickerSetColor(v);
					}
				});
			});
		}
	});
	
	$.djpcms.addDecorator({
		id:	"anchorbutton",
		description: "Decorate anchor as button using jQuery UI",
		decorate: function($this,config) {
			$('a.nice-button',$this).button();
		}
	});
	
	$.djpcms.addDecorator({
		id:	"autocomplete",
		description: "add ajax autocomplete to an input",
		decorate: function($this,config) {
			$('.djp-autocomplete',$this).each(function() {
				var el = $(this);
				var display  = $('input.lookup',el).attr('autocomplete','off');
				var divo    = $('div.options',el);
				var url     = $('a',divo).attr('href');
				var sep		= $('span.separator',divo);
				var name	= $('span.name',divo);
				if(name.length) {
					display.attr('_lookup',name.html());
				}
				var inline  = false;
				if(sep.length) {
					sep = sep.html();
				}
				else {
					sep = ' ';
				}
				if($('span.inline',divo).length) {
					inline = true;
				}
				divo.remove();
				if(display && url) {
					var opts = 	{
						delay:10,
		                minChars:2,
		                matchSubset:1,
		                autoFill:false,
		                matchContains:1,
		                cacheLength:10,
		                selectFirst:true,
		                maxItemsToShow:10,
		                formatItem: function(data, i, total) {
		        			return data[1];
		        		}
					};
					if(display.hasClass('multi')) {
						opts.multiple = true;
						opts.multipleSeparator = sep || " ";
						if(!inline) {
							el.mousedown(function (e) {
								e.stopPropagation();    
							}).mouseup(function(e) {
								var originalElement = e.originalTarget || e.srcElement;
								try {
									var al = $(originalElement);
									if(al.hasClass('deletable')) {
										al.parent().remove();
									}
								} catch(err) {}
							});
						}
					}
					display.autocomplete(url, opts);
					display.bind("result", function(el,data,bo) {
						var me   = $(this);
						var name = me.attr("_lookup");
						var next = me.next();
						var v    = data[2];
						if(me.hasClass("multi")) {
							var lbl = data[0];
							if(inline) {
								//me.val(me.val() + lbl);
							}
							else {
								var td  = $('<div class="to_delete"><input type="hidden" name="'+name+'" value="'+v+'"/><a href="#" class="deletable"></a>'+lbl+'</div>');
								next.append(td);
								me.val("");
							}
						}
						else {
							next.val(v);
						}
					});
				}
			});
		}
	});
		
})(jQuery);

