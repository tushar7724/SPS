// Copyright (c) 2018, TUSHAR TAJNE and contributors
// For license information, please see license.txt

frappe.ui.form.on('Period Master', {
	validate:function(frm){
		if(frm.doc.from_date && frm.doc.to_date){
			var first_date=  new  Date(frm.doc.from_date);
			var second_date= new  Date(frm.doc.to_date);
			var total_days= frappe.datetime.get_day_diff(second_date, first_date) + 1
			frm.set_value("total_days", total_days)
			frm.refresh_field("total_days")
		}
	}
});
