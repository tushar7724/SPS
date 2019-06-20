// Copyright (c) 2018, TUSHAR TAJNE and contributors
// For license information, please see license.txt

frappe.ui.form.on('Invoice', {
    onload: function(frm) {
        frm.events.party(frm);
	},
	add_contracts: function(frm) {
        var contracts_dialog = new frappe.ui.Dialog({
            title: __("Add Contracts"),
            fields: [
                {
                    "fieldtype": "Link",
                    "fieldname": "all_contract",
                    "options": "Contract",
                    "label": __("Contract"),
                    "reqd": 1,
                    "get_query": function () {
                        return {
                            filters: [
                                ['Contract', 'party_name', '=', cur_frm.doc.party],
                                ['Contract', 'name', 'not in', (cur_frm.doc.all_contract || "").split("\n")]
                            ]
                        }
                    }
                },
                {
                    "fieldtype": "Button",
                    "fieldname": "add",
                    "label": __("Add")
                }
            ]
        });
        contracts_dialog.get_input("add").on("click", function() {
            var contract_to_add = contracts_dialog.get_value("all_contract");
            if(contract_to_add) {
                var val = (cur_frm.doc.all_contract || "").split("\n").concat([contract_to_add]).join("\n");
                cur_frm.fields_dict.all_contract.set_model_value(val.trim());
                contracts_dialog.set_value("all_contract", "");
            }
            //contracts_dialog.hide();
            return false;
        });
        contracts_dialog.show();
	},
	remove_contract: function(frm) {
        var contracts_dialog = new frappe.ui.Dialog({
            title: __("Remove Contracts"),
            fields: [
                {
                    "fieldtype": "Link",
                    "fieldname": "all_contract",
                    "options": "Contract",
                    "label": __("Contract"),
                    "reqd": 1,
                    "get_query": function () {
                        return {
                            filters: [
                                ['Contract', 'party_name', '=', cur_frm.doc.party],
                                ['Contract', 'name', 'in', (cur_frm.doc.all_contract || "").split("\n")]
                            ]
                        }
                    }
                },
                {
                    "fieldtype": "Button",
                    "fieldname": "remove",
                    "label": __("Remove")
                }
            ]
        });
        contracts_dialog.get_input("remove").on("click", function() {
            var all_contract_to_delete = contracts_dialog.get_value("all_contract");
            if(all_contract_to_delete) {
                var new_arr=[];
                var str_val = (cur_frm.doc.all_contract || "").split("\n");
                for(var i=0; i < str_val.length;i++){
                    if(all_contract_to_delete != str_val[i]){
                        new_arr.push(str_val[i]);
                    }
                }
                var val = new_arr.join("\n");
                cur_frm.fields_dict.all_contract.set_model_value(val.trim());
                contracts_dialog.set_value("all_contract", "");
            }
            //contracts_dialog.hide();
            return false;
        });
        contracts_dialog.show();
	},
	clear_all_contracts: function(frm) {
        cur_frm.set_value('all_contract', "\n");
	},
	refresh: function(frm) {
		var att_frm_date = new Date(cur_frm.doc.invoice_date);
		var att_to_date = new Date(cur_frm.doc.to_date);
	    frappe.model.with_doc("Contract", cur_frm.doc.contract, function () {
            var contract = frappe.model.get_doc("Contract",cur_frm.doc.contract);
            $.each(contract.posting, function(index, row){
                var contract_start_date = new Date(contract.start_date);
                var contract_end_date = new Date(contract.end_date);
                var row_from_date = new Date(row.from_date);
                var row_to_date = new Date(row.to_date);
                //console.log("########### row_start_date ##########",row_from_date)
                //console.log("########### contract_end_date ##########",contract_end_date)
                if(row.employee != undefined){
                    if(att_frm_date >= contract_start_date && att_to_date <= contract_end_date && row_to_date >= att_frm_date && row_from_date <= att_to_date){
                        console.log("@@@@@@ Row Nos @@@@@@",index+1)
                    }
                }
                /*for(var i=0;i<row.quantity;i++){
                    var doc_posting_details = frappe.model.add_child(frm.doc, "People Posting", "posting_details");
                        doc_posting_details.srno = srno= srno+1
                        doc_posting_details.work_type = row.work_type
                        doc_posting_details.from_date = row.from_date
                        doc_posting_details.to_date = row.to_date
                }
                frm.refresh_field("posting_details");*/
            });
        });
	    setTimeout(function(){
            $('[data-fieldname="add_contracts"]').css("float", "left")
            $('[data-fieldname="remove_contract"]').css("float", "left").css("margin-left", "5px");
            $('[data-fieldname="clear_all_contracts"]').css("float", "left").css("margin-left", "5px");
        }, 200);

	/*    var tags= '<ul class="list-unstyled sidebar-menu"><li class="form-tags"> ' +
            ' <div class="tag-area"> ' +
                ' <div class="tag-line" style="position: relative"> ' +
                    ' <div class="tags-wrapper"> ' +
                        ' <ul class="tags-list"> ' +
                            ' <li class="tags-list-item">' +
                                '<div class="frappe-tag btn-group" data-tag-label="TUSHAR">' +
                                    '<button class="btn btn-default btn-xs toggle-tag" title="toggle Tag" data-tag-label="TUSHAR">TUSHAR</button>' +
                                    '<button class="btn btn-default btn-xs remove-tag" title="Remove Tag" data-tag-label="TUSHAR"><i class="fa fa-remove text-muted"></i></button>' +
                                '</div>' +
                            ' </li> ' +
                        ' </ul> ' +
                    ' </div> ' +
                ' </div> ' +
            ' </div> ' +
        ' </li></ul>'
        var all_contract = cur_frm.fields_dict['all_contract'];
        $('<div">'+tags+'</div>').appendTo($("<div>").css({"margin-bottom": "10px", "margin-top": "10px"}).appendTo(all_contract.wrapper));

        var label="TUSHAR";
        let $tag = $(`<div class="frappe-tag btn-group" data-tag-label="TUSHAR">
        <button class="btn btn-default btn-xs toggle-tag" title="toggle Tag" data-tag-label="TUSHAR">TUSHAR</button>
        <button class="btn btn-default btn-xs remove-tag" title="Remove Tag" data-tag-label="TUSHAR"><i class="fa fa-remove text-muted"></i></button>
        </div>`);

        let $removeTag = $tag.find(".toggle-tag");
        console.log("###### $tag ######",$tag)
        console.log("###### $removeTag ######",$removeTag)

        $removeTag.on("click", function() {
            console.log("###### $removeTag  click ######",$tag)
        });
        */


        //frm.events.party(frm);
        //var $btn_add_contracts = $('<button class="btn btn-sm btn-default">'+__("Add Contracts")+'</button>').appendTo($("<div>").css({"margin-bottom": "10px", "margin-top": "10px"}).appendTo(all_contract.wrapper));
        /*if(!$btn_add_contracts){
            var all_contract = cur_frm.fields_dict['party'];
            var $btn_add_contracts = $('<button class="btn btn-sm btn-default">'+__("Add Contracts")+'</button>').appendTo($("<div>").css({"margin-bottom": "10px", "margin-top": "10px"}).appendTo(all_contract.wrapper));
            $btn_add_contracts.on("click", function() {
                var contracts_dialog = new frappe.ui.Dialog({
                    title: __("Add Contracts"),
                    fields: [
                        {
                            "fieldtype": "Link",
                            "fieldname": "all_contract",
                            "options": "Contract",
                            "label": __("Contract"),
                            "reqd": 1,
                            "get_query": function () {
                                return {
                                    filters: [
                                        ['Contract', 'party_name', '=', cur_frm.doc.party],
                                        //['Contract', 'contract_name', 'not in', (cur_frm.doc.all_contract || "").split("\n")]
                                    ]
                                }
                            }
                        },
                        {
                            "fieldtype": "Button",
                            "fieldname": "add",
                            "label": __("Add")
                        },
                        {
                            "fieldtype": "Button",
                            "fieldname": "remove",
                            "label": __("Remove")
                        }
                    ]
                });
                contracts_dialog.get_input("add").on("click", function() {
                    var all_contract = contracts_dialog.get_value("all_contract");
                    if(all_contract) {
                        var val = (cur_frm.doc.all_contract || "").split("\n").concat([all_contract]).join("\n");
                        console.log("@@@@@@ After Add @@@@@",val.trim())
                        cur_frm.fields_dict.all_contract.set_model_value(val.trim());
                    }
                    contracts_dialog.hide();
                    return false;
                });
                contracts_dialog.get_input("remove").on("click", function() {
                    var all_contract = contracts_dialog.get_value("all_contract");
                    if(all_contract) {
                        var val = (cur_frm.doc.all_contract || "").split("\n").concat([]).join("\n").replace(all_contract + "\n","");
                        console.log("@@@@@@ After remove 1@@@@@",val)
                        cur_frm.fields_dict.all_contract.set_model_value(val.trim());
                    }
                    contracts_dialog.hide();
                    return false;
                });
                contracts_dialog.show();
            });
        }*/

	},
	party: function(frm) {
        cur_frm.fields_dict['party'].get_query = function(doc) {
            return {
				filters: [
                    ['Business Unit', 'bu_type', 'in', 'Customer, Client']
                ]
            }
        }
    }
});
