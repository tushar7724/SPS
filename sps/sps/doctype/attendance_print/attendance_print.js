// Copyright (c) 2019, TUSHAR TAJNE and contributors
// For license information, please see license.txt

frappe.ui.form.on('Attendance Print', {
	refresh: function(frm) {
		frm.set_query("site", function() {
            return {
                filters: {
                    'bu_type' : "Site"
                }
            }
        });
		cur_frm.fields_dict.contract.get_query = function(doc) {
            return {
                filters: { "docstatus" : 1, "status" : "Active" }
            }
        }
        frm.refresh_field("contract");
	}
});
