frappe.listview_settings['SPS Attendance'] = {
	add_fields: ["status","name"],
	get_indicator: function (doc) {
	    if (doc.docstatus === 1 && doc.status === "To Bill") {
			return [__("To Bill"), "orange", "status,=,To Bill"];

		}else if (doc.docstatus === 1 && doc.status === "Completed") {
			return [__("Completed"), "green", "status,!=,To Bill"];
		}
	},
	onload: function(listview) {
		listview.page.add_menu_item(__("Attendance Print Format"), function(){
				var dialog = new frappe.ui.Dialog({
                    title: __("Attendance Print Format"),
                    fields: [
                                {"fieldtype": "Select", "label": __("Type"),"options": "\nMonthly Attendance\nAttendance State Form\nAttendance Centrial Form XVI", "fieldname": "print_type","reqd": 1},
								{"fieldtype": "Link", "label":__("Period"), "options": "Payroll Period", "fieldname": "period", "reqd": 1}, 
								{"fieldtype": "Link", "label": __("Customer"), "options": "Customer",  "fieldname": "customer"},
								{"fieldtype": "Link", "label": __("Site"), "options": "Business Unit", "fieldname": "site"},
								{"fieldtype": "Link", "label": __("Contract"), "options": "Contract",  "fieldname": "contract"},
                                {"fieldtype": "Button", "label": __("Show Prints"), "fieldname": "show_print"},
                            ]
                });
                dialog.show()
				dialog.fields_dict.show_print.input.onclick = function(){
					var data= dialog.get_values()
					if (data){
							console.log("")
						}
				}
			});
	}
};

