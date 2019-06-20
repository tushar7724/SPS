// Copyright (c) 2019, TUSHAR TAJNE and contributors
// For license information, please see license.txt
frappe.ui.form.on('Payroll Process', {
    refresh: function(frm) {
		frm.events.customer(frm);
		if(frm.doc.period && frm.doc.addtional_filter == "attendance"){
			frm.set_query("attendance", function() {
				return {filters : {'docstatus': 1, 'attendance_period': cur_frm.doc.period}}
			});
		}
		if (frm.doc.docstatus == 1) {
			if(!frm.is_new()) {
				frm.add_custom_button(__("Payroll Process"), function(){
					frappe.call({
						method:"create_processed_payroll_entry",
						doc: cur_frm.doc,
						callback:function(r){
							//frappe.msgprint("Payroll Process Done Successfully")
							if (r.message==='queued') {
                                frappe.show_alert({
                                    message: __("Payroll Process creation has been queued."),
                                    indicator: 'orange'
                                });
                            } else {
                                frappe.show_alert({
                                    message: __("{0} Payroll Created Successfully.", [r.message]),
                                    indicator: 'green'
                                });
                            }
						}
					});
				}).toggleClass('btn-primary');
				//frm.page.clear_primary_action();
				frm.add_custom_button(__("Make Salary Slips"),
					function() {
						//frm.events.get_employee_details(frm);
						var dialog = new frappe.ui.Dialog({
                            title: __("Select Criteria to Create Payout."),
                            fields: [
                                /*{"fieldtype": "Data", "label": __("Pay Status"), "fieldname": "pay_slip_status","reqd": 0},
                                {"fieldtype": "Data", "label": __("Branch"), "fieldname": "branch","reqd": 0},*/
                                {
                                    fieldtype: "Link",
                                    fieldname: "employee",
                                    label: __("Employee"),
                                    options: "Employee",
                                    reqd: 0,
                                },
                                {"fieldtype": "Column Break", "fieldname": "columnbreak1"},
                                {
                                    fieldtype: "Link",
                                    fieldname: "wage_rule",
                                    label: __("Salary Structure"),
                                    options: "Salary Structure",
                                    reqd: 0,
                                },
                                {"fieldtype": "Section Break", "fieldname": "sectionbreak1"},
                                {"fieldtype": "Button", "label": __("Make Salary Slips"), "fieldname": "make_payout","description": ""}
                            ]
                        });
                        //dialog.fields_dict.make_payout.addClass("btn-primary");
                        dialog.fields_dict.make_payout.input.onclick = function() {
                            var values = dialog.get_values();

                            frappe.call({
                                method:"create_payout",
                                doc: cur_frm.doc,
                                args: {
                                    employee: values.employee,
                                    wage_rule: values.wage_rule
                                },
                                callback: function(r) {
                                    console.log("###### pp_list#####",r.message)
                                    //frappe.msgprint(__("Salary Slips Successfully Created"))
                                    if (r.message==='queued') {
                                        frappe.show_alert({
                                            message: __("Salary Slips creation has been queued."),
                                            indicator: 'orange'
                                        });
                                    } else {
                                        frappe.show_alert({
                                            message: __("{0} Salary Slips Created.", [r.message]),
                                            indicator: 'green'
                                        });
                                    }
                                },
                            });
                            dialog.hide();
                        }
                        dialog.show();
					}
				).toggleClass('btn-primary');
				frm.add_custom_button(__("Delete Processed Entries"), function(){
					frappe.confirm('Are you sure you want to delete records?',
                        function(){
                            frappe.call({
                                method: "delete_processed_entry",
                                doc: cur_frm.doc,
                                callback:function(r){
                                    frappe.msgprint(r.message)
                                    frm.reload_doc();
                                }
                            });
                        },
                        function(){
                            window.close();
                        }
                    )
				}).toggleClass('btn-primary');
			}
		}
	},
	period:function(frm){
		if(cur_frm.doc.period != undefined){
			frappe.model.with_doc("Payroll Period", cur_frm.doc.period, function () {
				var period = frappe.model.get_doc("Payroll Period",cur_frm.doc.period);
				frm.set_value("pay_type", period.pay_type)
				frm.refresh_field("pay_type")
				frm.set_value("start_date", period.start_date);
				frm.refresh_field("start_date");
				frm.set_value("end_date",    period.end_date);
				frm.refresh_field("end_date");
				frm.set_value("total_days", period.total_days);
				frm.refresh_field("total_days");
				frm.set_value("pay_date", period.pay_date);
				frm.refresh_field("pay_date");
				
		    });
        	}
		if (frm.doc.period == "" && frm.doc.period == undefined){
			cur_frm.doc.additional_filter= ""
			frm.refresh_field("additional_filter")
			cur_frm.doc.attendance = ""
			frm.refresh_field("attendance")
			cur_frm.doc.customer = ""
			frm.refresh_field("customer")
			cur_frm.doc.site = ""
			frm.refresh_field("site")
		}
		
	},
	additional_filter:function(frm){
		if (frm.doc.additional_filter ==  "Customer"){
			frm.set_df_property("customer", "reqd", 1);
			frm.set_df_property("attendance", "reqd", 0);
		}
		else if (frm.doc.additional_filter == "Attendance"){
			frm.set_df_property("attendance", "reqd", 1);
			frm.set_df_property("customer", "reqd", 0);
			frm.set_query("attendance", function() {
                            return {filters : {'docstatus': 1, 'attendance_period': cur_frm.doc.period}}
                        });
			
		}
		else{
			frm.set_df_property("customer", "reqd", 0);
			frm.set_df_property("attendance", "reqd", 0);
		}
	},
	customer:function(frm){
		if(cur_frm.doc.customer == "" || cur_frm.doc.customer == undefined){
			cur_frm.doc.site = ""
                	frm.refresh_field("site")
		}
		var filters =  {
                        'bu_name': 'None',
                        'bu_type': 'None'
                }
		if(frm.doc.customer){
                    frappe.model.with_doc("Customer", cur_frm.doc.customer, function() {
                        var customer = frappe.model.get_doc("Customer", cur_frm.doc.customer);
                        if(customer != undefined && customer.customer_code != undefined && customer != "" && customer.disabled == 0){
                            filters =  {
                                'business_unit': customer.customer_code,
                                'bu_type': 'Site'
                            }
                        }
                        frm.set_query("site", function() {
                            return {filters : filters}
                        });
                    });
                }
		
	},
	site:function(frm){
		frm.events.customer(frm)
		if(!frm.doc.customer){
			frappe.msgprint("Please select Customer")
			cur_frm.doc.site = "" 
			frm.refresh_field("site")
		}
	},
	attendance:function(frm){
		if(!frm.doc.period){
			frappe.msgprint("Please Select Period")
                        cur_frm.doc.attendance = ""
                        frm.refresh_field("attendance")
		}
	}/*,
	on_submit: function(frm){
		frappe.call({
			method:"create_processed_payroll_entry",
			doc: cur_frm.doc,
			callback:function(r){
				frappe.msgprint("Payroll Process Done Successfully")
			}
		});
	}*/
});
