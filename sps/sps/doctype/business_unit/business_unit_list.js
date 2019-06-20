frappe.listview_settings['Business Unit']= {
        onload: function(listview) {
                listview.page.add_menu_item(__("Fetch/Update Bu Data"), function(frm) {
                        frappe.call({
                                method: "sps.sps.doctype.business_unit.business_unit.get_youtility_data",
                                args:{
                                        "param": {
                                        "web_service"      : "Business Unit",

                                        }
                                },
                                callback: function(r){
                                msgprint(r)
                                //cur_list.refresh()
                                }
                        });

                });
       }
};
