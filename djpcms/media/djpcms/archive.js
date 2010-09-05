

(function($) {
    $.djpcms.addDecorator({
        id:"archive-list",
        decorate: function($this, config) {
    		$(".archive-list",$this).accordion({collapsible: true});
        }
    });
})(jQuery);