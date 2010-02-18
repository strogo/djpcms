

function cmstree(elem,url_){
	var columns;
	var ctree = $(elem).coltree({
		debug: true,
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
		data : {
			type : "json",
			async : true,
			opts : {
				method : "POST",
				url : url_
			}
		},
		ui: {
			theme_name : "smooth"
		},
		callback : {
			ondata: function(data, tree_obj) {
				var sites = data.sites;
				columns = data.columns;
				return sites;
			},
			onparse: function(STR,TREE_OBJ) {
				return STR;
			},
			onload: function(TREE_OBJ) {
				var top = '<ul class="header"><li>';
				$.each(columns, function(c,namec) {
					var cn = '<div class="tcolumn tcolumn-' + c + '">' + namec + '</div>';
					if(c == 0) {
						top += '<div class="coltitle">' + cn + '</div><div class="colsdata">';
					}
					else {
						top += cn;
					}
				});
				top += '</div></li></ul>';
				$(elem+' ul').before(function(el) {
					if(top) {
						var stop = top;
						top = '';
						return stop;
					}
				});
				$(elem+' div.colsdata div.tcolumn').width(100);
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
				/*moveTreeItem(what, item_id, target_id, position, false);*/
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
