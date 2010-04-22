
(function($) {
	
	$.djpcms.addDecorator({
		id:	"autocomplete",
		description: "add ajax autocomplete to a input",
		decorate: function($this,config) {
			$('.djp-autocomplete',$this).each(function() {
				var el = $(this);
				var display  = $('input.lookup',el).attr('autocomplete','off');
				var divo    = $('div.options',el);
				var url     = $('a',divo).attr('href');
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
						opts.multipleSeparator = ", ";
						el.click(function(e) {
							var originalElement = e.originalTarget || e.srcElement;
							try {
								var al = $(originalElement);
								if(al.hasClass('deletable')) {
									al.parent().remove();
								}
							} catch(err) {}
						});
					}
					display.autocomplete(url, opts);
					display.bind("result", function(el,data,bo) {
						var me   = $(this);
						var name = me.attr("id").split("-")[1];
						var next = me.next();
						var v    = data[2];
						if(me.hasClass("multi")) {
							var lbl = data[0];
							var td  = $('<div class="to_delete"><input type="hidden" name="'+name+'" value="'+v+'"/><a href="#" class="deletable"></a>'+lbl+'</div>');
							next.append(td);
							//next.append(new Option(lbl,v,true));
							me.val("");
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
