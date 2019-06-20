// Copyright (c) 2018, TUSHAR TAJNE and contributors
// For license information, please see license.txt

frappe.ui.form.on('Wage Rule', {
    onload: function (frm) {
        //frm.refresh_field('to_date')
		//frm.doc.bank_name = '';
		//frm.doc.start_date = '';
		//frm.doc.end_date = '';self.is_new() and self.amended_from
	},
	refresh: function(frm) {
	    if(cur_frm.doc.docstatus == 1 && cur_frm.doc.status == "Active") {
		    //frm.add_custom_button(__('Make Revision'),function() { frm.btn_make_revision(doc, dt, dn) });
            //frm.add_custom_button(__('Calculate Costing'),function() { frm.calculate_costing(doc, dt, dn) });
            if(frm.doc.docstatus == 1){
                frm.add_custom_button(__('Make Revision'), function () {
                    //refresh_field('revision_number');
                    //frm.set_value('revision_number', cur_frm.doc.revision_number + 1);
                    //refresh_field('revision_number');
                    frm.amend_doc();
                    //frm.copy_doc();
                });
            }
            if(frm.doc.docstatus == 1){
                frm.add_custom_button(__('Calculate Costing'), function () {
                    frm.print_doc();
                });
            }
        }
        //console.log("#######amended_from##########",frm.doc.amended_from);
		//console.log("#######docstatus##########",frm.doc.docstatus);
		//console.log("#######revision_number##########",frm.doc.revision_number);

		if (frm.doc.amended_from != undefined && cur_frm.doc.docstatus == 0){
		    console.log("@@@@@@@@@ frm.doc.amended_from @@@@@@@@@@@",frm.doc.amended_from)
		    frappe.call({
                method: "frappe.client.get",
                args: {
                    doctype: "Wage Rule",
                    name: frm.doc.amended_from
                },
                callback(r) {
                    if(r.message) {
                        var prev_doc = r.message;
                        //console.log("@@@@ prev_doc.revision_number @@@@@@",prev_doc.revision_number);
                        //console.log("@@@@ prev_doc status @@@@@@",prev_doc.docstatus);
                        if(prev_doc.docstatus == 1){
                            frm.set_value('revision_number', prev_doc.revision_number + 1)
                            frm.refresh_field('revision_number')
                        }else if(prev_doc.docstatus == 2){
                            frm.set_value('revision_number', prev_doc.revision_number)
                            frm.refresh_field('revision_number')
                        }
                    }
                }
            });
		}
		if(cur_frm.doc.docstatus == 0) {
		    //frm.set_value('to_date', frappe.datetime.add_months("2100-12-31",0))
		    //frm.refresh_field('to_date')

		    frm.set_value('revision_date', frappe.datetime.get_today())
		    frm.refresh_field('revision_date')
		}
	}
});
