// Copyright (c) 2019, TUSHAR TAJNE and contributors
// For license information, please see license.txt

frappe.ui.form.on('Attendance Sheet', {
	refresh: function(frm) {

	},
	period: function(frm) {
        frappe.model.with_doc("Payroll Period", cur_frm.doc.period, function() {
            var period = frappe.model.get_doc("Payroll Period", cur_frm.doc.period);
            frm.set_value('start_date', period.start_date)
            frm.set_value('end_date', period.end_date)
            frm.refresh_field('start_date')
            frm.refresh_field('end_date')
        });
	}
});
