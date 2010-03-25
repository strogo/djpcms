
(function($) {
	
	$.djpcms.addDecorator({
		id:	"autocomplete",
		description: "add ajax autocomplete to a input",
		decorate: function($this,config) {
			$('.djp-autocomplete',$this).each(function() {
				var el = $(this);
				var inputs  = $('input',el);
				var url    = $('a',el).attr('href');
				var search = [];
				$('span',el).each(function(i) {
					search[i] = this.innerHTML;
				});
				if(inputs.length == 2 && url && search) {
					var display = $(inputs[0]);
					var input   = $(inputs[1]).hide();
					el.after(display).remove();
					display.after(input);
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
		        			return data[0];
		        		}
					};
					display.autocomplete(url, opts);
					display.bind("result", function(el,data,bo) {
						input.val(data[1]);
					});
				}
			});
		}
	});
	
})(jQuery);
