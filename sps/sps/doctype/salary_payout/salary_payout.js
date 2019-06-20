// Copyright (c) 2019, TUSHAR TAJNE and contributors
// For license information, please see license.txt

frappe.ui.form.on('Salary Payout', {
	refresh:function(frm){
		if(frm.doc.docstatus > 0){
			cur_frm.set_df_property("number_of_employee", "read_only", true);
		}
	}
});
