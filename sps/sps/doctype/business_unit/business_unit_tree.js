frappe.treeview_settings["Business Unit"] = {
	breadcrumbs: "Business Unit",
	title: __("Business Unit"),
	get_tree_root: false,
	filters: [{
		fieldname: "bu_type",
		fieldtype:"Select",
		options: ["Client"],
		label: __("Type"),
		default: "Client"
	}],
	root_label: "Business Unit",
	get_tree_nodes: 'sps.sps.doctype.business_unit.business_unit.get_children',
	//add_tree_node: 'erpnext.accounts.utils.add_ac',
	menu_items:[
		{
			label: __('New Business Unit'),
			action: function() { frappe.new_doc("Business Unit", true) },
			condition: 'frappe.boot.user.can_create.indexOf("Business Unit") !== -1'
		}
	],
	fields: [
	    {
		    fieldtype:'Select',
		    fieldname:'bu_type',
		    label:__('Business Unit Type'),
		    options:["Client","Zone","Branch","Customer","Site"],
		    reqd:true,
        },
	    {
		    fieldtype:'Data',
		    fieldname:'bu_code',
		    label:__('Business Unit Code'),
		    reqd:true
        },
		{
		    fieldtype:'Data',
		    fieldname:'bu_name',
		    label:__('Business Unit Name'),
		    reqd:true
        },
        {
		    fieldtype:'Link',
		    fieldname:'business_unit',
		    options:'Business Unit',
		    label:__('Parent'),
		    reqd:true,
		    onchange: function(frm) {
		    }
        },
        {
		    fieldtype:'Column Break',
		    fieldname:'column_break_7',
        },{
		    fieldtype:'Check',
		    fieldname:'is_group',
		    label:__('Is Group')
        },{
		    fieldtype:'Check',
		    fieldname:'enable',
		    label:__('Enable'),
		    default:1
        }
	],
	ignore_fields:["business_unit"],
	onload: function(treeview) {
		frappe.treeview_settings['Business Unit'].page = {};
		$.extend(frappe.treeview_settings['Business Unit'].page, treeview.page);
		function get_company() {
			return treeview.page.fields_dict.company.get_value();
		}
	},
	extend_toolbar: false
}


