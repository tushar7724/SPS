// Copyright (c) 2018, TUSHAR TAJNE and contributors
// For license information, please see license.txt

frappe.ui.form.on('Posting', {
	refresh: function(frm) {
	},
	contract: function(frm) {
        if (frm.doc.contract) {
            frappe.model.clear_table(frm.doc, "posting_details");
			frappe.model.with_doc("Contract", cur_frm.doc.contract, function () {
				var contract = frappe.model.get_doc("Contract",cur_frm.doc.contract);
                var srno=0
                $.each(contract.contract_details, function(index, row){
                    for(var i=0;i<row.quantity;i++){
                        var doc_posting_details = frappe.model.add_child(frm.doc, "People Posting", "posting_details");
                            doc_posting_details.srno = srno= srno+1
                            doc_posting_details.work_type = row.work_type
                            doc_posting_details.from_date = row.from_date
                            doc_posting_details.to_date = row.to_date
                    }
                    frm.refresh_field("posting_details");
                });
			});
		}
	}
});

