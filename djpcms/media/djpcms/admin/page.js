(function ($) {
	$.extend($.tree.datastores, {
		"jsontable" : function () {
			return {
				get		: function(obj, tree, opts) { 
					var _this = this;
					if(!obj || $(obj).size() == 0) obj = tree.container.children("ul").children("li");
					else obj = $(obj);

					if(!opts) opts = {};
					if(!opts.outer_attrib) opts.outer_attrib = [ "id", "rel", "class" ];
					if(!opts.inner_attrib) opts.inner_attrib = [ ];

					if(obj.size() > 1) {
						var arr = [];
						obj.each(function () {
							arr.push(_this.get(this, tree, opts));
						});
						return arr;
					}
					if(obj.size() == 0) return [];

					var json = { attributes : {}, data : {} };
					if(obj.hasClass("open")) json.data.state = "open";
					if(obj.hasClass("closed")) json.data.state = "closed";

					for(var i in opts.outer_attrib) {
						if(!opts.outer_attrib.hasOwnProperty(i)) continue;
						var val = (opts.outer_attrib[i] == "class") ? obj.attr(opts.outer_attrib[i]).replace(/(^| )last( |$)/ig," ").replace(/(^| )(leaf|closed|open)( |$)/ig," ") : obj.attr(opts.outer_attrib[i]);
						if(typeof val != "undefined" && val.toString().replace(" ","").length > 0) json.attributes[opts.outer_attrib[i]] = val;
						delete val;
					}
					
					if(tree.settings.languages.length) {
						for(var i in tree.settings.languages) {
							if(!tree.settings.languages.hasOwnProperty(i)) continue;
							var a = obj.children("a." + tree.settings.languages[i]);
							if(opts.force || opts.inner_attrib.length || a.children("ins").get(0).style.backgroundImage.toString().length || a.children("ins").get(0).className.length) {
								json.data[tree.settings.languages[i]] = {};
								json.data[tree.settings.languages[i]].title = tree.get_text(obj,tree.settings.languages[i]);
								if(a.children("ins").get(0).style.className.length) {
									json.data[tree.settings.languages[i]].icon = a.children("ins").get(0).style.className;
								}
								if(a.children("ins").get(0).style.backgroundImage.length) {
									json.data[tree.settings.languages[i]].icon = a.children("ins").get(0).style.backgroundImage.replace("url(","").replace(")","");
								}
								if(opts.inner_attrib.length) {
									json.data[tree.settings.languages[i]].attributes = {};
									for(var j in opts.inner_attrib) {
										if(!opts.inner_attrib.hasOwnProperty(j)) continue;
										var val = a.attr(opts.inner_attrib[j]);
										if(typeof val != "undefined" && val.toString().replace(" ","").length > 0) json.data[tree.settings.languages[i]].attributes[opts.inner_attrib[j]] = val;
										delete val;
									}
								}
							}
							else {
								json.data[tree.settings.languages[i]] = tree.get_text(obj,tree.settings.languages[i]);
							}
						}
					}
					else {
						var a = obj.children("a");
						json.data.title = tree.get_text(obj);

						if(a.children("ins").size() && a.children("ins").get(0).className.length) {
							json.data.icon = a.children("ins").get(0).className;
						}
						if(a.children("ins").size() && a.children("ins").get(0).style.backgroundImage.length) {
							json.data.icon = a.children("ins").get(0).style.backgroundImage.replace("url(","").replace(")","");
						}

						if(opts.inner_attrib.length) {
							json.data.attributes = {};
							for(var j in opts.inner_attrib) {
								if(!opts.inner_attrib.hasOwnProperty(j)) continue;
								var val = a.attr(opts.inner_attrib[j]);
								if(typeof val != "undefined" && val.toString().replace(" ","").length > 0) json.data.attributes[opts.inner_attrib[j]] = val;
								delete val;
							}
						}
					}

					if(obj.children("ul").size() > 0) {
						json.children = [];
						obj.children("ul").children("li").each(function () {
							json.children.push(_this.get(this, tree, opts));
						});
					}
					return json;
				},
				parse	: function(data, tree, opts, callback) { 
					if(Object.prototype.toString.apply(data) === "[object Array]") {
						var str = '';
						for(var i = 0; i < data.length; i ++) {
							if(typeof data[i] == "function") continue;
							str += this.parse(data[i], tree, opts);
						}
						if(callback) callback.call(null, str);
						return str;
					}

					if(!data || !data.data) {
						if(callback) callback.call(null, false);
						return "";
					}

					var str = "<li ";
					var cls = false;
					if(data.attributes) {
						for(var i in data.attributes) {
							if(!data.attributes.hasOwnProperty(i)) continue;
							if(i == "class") {
								str += " class='" + data.attributes[i] + " ";
								if(data.state == "closed" || data.state == "open") str += " " + data.state + " ";
								str += "' ";
								cls = true;
							}
							else str += " " + i + "='" + data.attributes[i] + "' ";
						}
					}
					if(!cls && (data.state == "closed" || data.state == "open")) str += " class='" + data.state + "' ";
					str += ">";

					$.each(data.data, function(i,vals) {
						$.each(vals.data,function(j,val) {
							if(j==0) {
								var attr = {};
								attr["class"] = "tcolumn-" + j;
								attr["href"] = "";
								attr["style"] = "";
								/*
								if((typeof data.data.attributes).toLowerCase() != "undefined") {
									for(var i in data.data.attributes) {
										if(!data.data.attributes.hasOwnProperty(i)) continue;
										if(i == "style" || i == "class")	attr[i] += " " + data.data.attributes[i];
										else								attr[i]  = data.data.attributes[i];
									}
								}*/
								str += "<a";
								for(var i in attr) {
									if(!attr.hasOwnProperty(i)) continue;
									str += ' ' + i + '="' + attr[i] + '" ';
								}
								str += ">";
								if(val.icon) {
									str += "<ins " + (val.icon.indexOf("/") == -1 ? " class='" + val.icon + "' " : " style='background-image:url(\"" + val.icon + "\");' " ) + ">&nbsp;</ins>";
								}
								else str += "<ins>&nbsp;</ins>";
								str += ( (typeof val.title).toLowerCase() != "undefined" ? val.title : val ) + "</a>";
							}
							else {
								str += '<span class="tcolumn-' + j + '">' + val + "</span>";
							}
						});
					});
					if(data.children && data.children.length) {
						str += '<ul>';
						for(var i = 0; i < data.children.length; i++) {
							str += this.parse(data.children[i], tree, opts);
						}
						str += '</ul>';
					}
					str += "</li>";
					if(callback) callback.call(null, str);
					return str;
				},
				load	: function(data, tree, opts, callback) {
					if(opts.static) {
						callback.call(null, opts.static);
					} 
					else {
						$.ajax({
							'type'		: opts.method,
							'url'		: opts.url, 
							'data'		: data, 
							'dataType'	: "json",
							'success'	: function (d, textStatus) {
								callback.call(null, d);
							},
							'error'		: function (xhttp, textStatus, errorThrown) { 
								callback.call(null, false);
								tree.error(errorThrown + " " + textStatus); 
							}
						});
					}
				}
			}
		}
	});
})(jQuery);


function cmstree(elem,url_){
	var columns;
	var tree = $(elem).tree({
		data : {
			type : "jsontable",
			async : true,
			opts : {
				method : "POST",
				url : url_
			}
		},
		ui: {
			theme_name : "appletable"
		},
		callback : {
			ondata: function(data, tree_obj) {
				var sites = data.sites;
				columns = data.columns;
				return sites;
			},
			onparse: function(STR,TREE_OBJ) {
			    var top = '<li class="tabletree-header">';
				$.each(columns, function(c,namec) {
					top += '<span class="tcolumn-' + c + '">' + namec + '</span>';
				});
				top += '</li>';
				return top + STR;
			},
			onload: function(TREE_OBJ) {
				if(columns) {
					$.each(columns, function(c,namec) {
						$('.tcolumn-' + c).width(100);
					});
				}
			}
		}
	});
	/*
	tree = new tree_component();
	var options = {
		rules: {
			clickable: "all",
			renameable: "none",
			deletable: "all",
			creatable: "all",
			draggable: "all",
			dragrules: "all",
			droppable: "all",
			metadata : "mdata",
			use_inline: true
			//droppable : ["tree_drop"]
		},
		path: false,
		ui: {
			dots: true,
			rtl: false,
			animation: 0,
			hover_mode: true,
			theme_path: false,
			theme_name: "default",
			a_class: "title"
		},
		cookies : {},
		callback: {
			beforemove  : function(what, where, position, tree) {
				item_id = what.id.split("page_")[1];
				target_id = where.id.split("page_")[1];
				old_node = what;
				if($(what).parent().children("li").length > 1){
					if($(what).next("li").length){
						old_target = $(what).next("li")[0];
						old_position = "right";
					}
					if($(what).prev("li").length){
						old_target = $(what).prev("li")[0];
						old_position = "left";
					}
				}else{
					if($(what).attr("rel") != "topnode"){
						old_target = $(what).parent().parent()[0];
						old_position = "inside";
					}
				}
				
				addUndo(what, where, position);
				return true; 
			},
			onmove: function(what, where, position, tree){
				item_id = what.id.split("page_")[1];
				target_id = where.id.split("page_")[1];
				if (position == "before") {
					position = "left";
				}else if (position == "after") {
					position = "right";
				}else if(position == "inside"){
					position = "last-child";
				}
				moveTreeItem(what, item_id, target_id, position, false);
			},
			onchange: function(node, tree){
				var url = $(node).find('a.title').attr("href");
				self.location = url;
			}
		}
	};
	
	
	if (!$($("div.tree").get(0)).hasClass('root_allow_children')){
		// disalow possibility for adding subnodes to main tree, user doesn't
		// have permissions for this
		options.rules.dragrules = ["node inside topnode", "topnode inside topnode", "node * node"];
	}
	
	//dragrules : [ "folder * folder", "folder inside root", "tree-drop * folder" ],
        
	tree.init($("div.tree"), options);
	*/
};
