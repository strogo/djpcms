(function($) {
	
	/**
	 * Right-click jQuery plugin
	 * Adapted from http://abeautifulsite.net/2008/05/jquery-right-click-plugin/
	 */
	$.extend($.fn, {
		
		rightClick: function(handler) {
			$(this).each( function() {
				$(this).mousedown( function(e) {
					var evt = e;
					$(this).mouseup( function() {
						$(this).unbind('mouseup');
						if( evt.button == 2 ) {
							handler.call( $(this), evt );
							return false;
						} else {
							return true;
						}
					});
				});
				$(this)[0].oncontextmenu = function() {
					return false;
				}
			});
			return $(this);
		},		
		
		rightMouseDown: function(handler) {
			$(this).each( function() {
				$(this).mousedown( function(e) {
					if( e.button == 2 ) {
						handler.call( $(this), e );
						return false;
					} else {
						return true;
					}
				});
				$(this)[0].oncontextmenu = function() {
					return false;
				}
			});
			return $(this);
		},
		
		rightMouseUp: function(handler) {
			$(this).each( function() {
				$(this).mouseup( function(e) {
					if( e.button == 2 ) {
						handler.call( $(this), e );
						return false;
					} else {
						return true;
					}
				});
				$(this)[0].oncontextmenu = function() {
					return false;
				}
			});
			return $(this);
		},
		
		noContext: function() {
			$(this).each( function() {
				$(this)[0].oncontextmenu = function() {
					return false;
				}
			});
			return $(this);
		}
		
	});
	
	
	
	/**
	 * Create a right click menu element To add, delete and rename subfolders
	 */
	$.fn.rightClickMenu = function(holder, options_) {
		var current = null;
		var holder  = holder;
		var $this   = this;
		
		var options = {
			x: 20,
			y: 10,
			fade: 300,
			actionClass: 'rightClickAction',
			selectedClass: 'rclk',
			menuClass: 'rightClickMenu',
			actions: []
		}
		
		/**
		 * Display the right-click menu at the portfolio element selected
		 * 
		 * @param x - float, the x coordinate
		 * @param y - float, the y coordinate
		 * @param el - jQuery Portfolio Node
		 * @return this
		 */
		options.display = function(x, y, el) {
			$.each(options.actions, function(i,v) {
				if(v.available(el,holder)) {
					v.element.show();
				}
				else {
					v.element.hide();
				}
			});
			$this.hide().css({top: y + options.y, left: x + options.x}).fadeIn(options.fade);
		};
		
		options = $.extend(true, options_, options);
		
		holder.append($this.hide().addClass(options.menuClass));
		var elem    = $this[0];
		var actions = options.actions;
		var adict	= {};
		var ul = $('<ul></ul>').appendTo($this.html(''));
		
		$.each(actions, function(i,v) {
			var name  = v.name;
			var descr = v.description || name;
			var act = $('<a name="' + name + '">' + descr + '</a>').addClass(options.actionClass);
			v.element = $('<li></li>').appendTo(ul).append(act);
			adict[name] = v;
			act.click(function(e) {
				v.onclick(current);
			});
		});
		
		function clear() {
			if(current) {
				var sc = options.selectedClass;
				if(sc) {
					current.removeClass(sc);
				}
				$this.hide();
				current = null;
			}
		}
		
		this.register = function(elems, handler_, actions_) {
			var sc = options.selectedClass;
			var handler = handler_ || function(elem){return true;}
			var actions = actions || {};
			
			elems.rightMouseDown(function(ev,el) {
				var elem = $(this);
				clear();
				if(sc) {
					elems.removeClass(sc);
					elem.addClass(sc);
				}
				if(actions.down) {
					actions.down(elem);
				}
				if(handler(elem)) {
					var pos  = this.offset();
					current  = elem;
					current.addClass(sc);
					options.display(pos.left,pos.top,current);
				}
			});
			if(actions.up) {
				elems.rightMouseUp(actions.up);
			}
			
		};
		
		
		$(document).rightMouseDown(function(ev,el) {
			clear();
		}).click(function(ev,el) {
			clear();
		});
		
		return $this;
	};
	
		
})(jQuery);
