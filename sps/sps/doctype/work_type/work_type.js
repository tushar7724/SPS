// Copyright (c) 2018, TUSHAR TAJNE and contributors
// For license information, please see license.txt

frappe.ui.form.on('Work Type', {
	create_item: function(frm) {
		if (!frm.doc.work_type_name){
			frappe.throw(__("Please enter Work Type Name"))
		}else{
		    frappe.call({
                method: "erpnext.hr.doctype.work_type.work_type.create_item",
                args: { work_type: frm.doc.name},
                callback: function(r){
                    frm.set_value("item", r.message)
                    cur_frm.save();
                }
            });
		}
	}
});
