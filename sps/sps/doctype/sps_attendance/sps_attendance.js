// Copyright (c) 2018, TUSHAR TAJNE and contributors
// For license information, please see license.txt

frappe.ui.form.on('SPS Attendance', {
    /*onload:function(frm){
        var contract=cur_frm.doc.contract;
        frm.set_value('contract', "")
        frm.refresh_field("contract");
        frm.set_value('contract', contract)
        frm.refresh_field("contract");
        frm.save('Update');
    },*/
    refresh:function(frm){
        if(frm.doc.__islocal != 1 && frm.doc.contract){
            cur_frm.set_df_property("get_posting_details", "hidden", false);
        }else{
            cur_frm.set_df_property("get_posting_details", "hidden", true);
        }
        if(frm.doc.docstatus == 1){
            cur_frm.set_df_property("get_posting_details", "hidden", true);
        }
        $(".grid-add-row").hide();
        if(frm.doc.docstatus == 1){
            if(frm.doc.total_pd > 0 && frm.doc.total_pd_ed < 1 && frm.doc.total_pd_ed_wo < 1){
                frm.set_value("total_pd_ed", frm.doc.total_pd + frm.doc.total_ed);
                frm.set_value("total_pd_ed_wo", frm.doc.total_pd + frm.doc.total_ed + frm.doc.total_wo);
                frm.save('Update');
            }
        }
        if(cur_frm.docstatus==0){
			console.log("###")	
            //frm.events.contract(frm);
        }
    },
    attendance_period: function(frm) {
        if(cur_frm.doc.attendance_period != undefined){
            frappe.model.with_doc("Payroll Period", cur_frm.doc.attendance_period, function () {
                var period = frappe.model.get_doc("Payroll Period",cur_frm.doc.attendance_period);
                frm.set_value("start_date", period.start_date);
                        frm.refresh_field("start_date");
                frm.set_value("end_date",    period.end_date);
                        frm.refresh_field("end_date");
                frm.set_value("total_days", period.total_days);
                frm.refresh_field("total_days");
                frm.set_value('customer', "");
            });
        }
    },
    customer: function(frm){
        frm.set_value('contract', "");
        frm.set_value('branch', "");
        cur_frm.fields_dict.contract.get_query = function(doc) {
            return {
            filters:{"party_name" : cur_frm.doc.customer, "docstatus" : 1, "status" : "Active"}
            }
        }
        frappe.model.with_doc("Business Unit", cur_frm.doc.attendance_period, function () {
            var period = frappe.model.get_doc("Payroll Period",cur_frm.doc.attendance_period);
            frm.set_value("start_date", period.start_date);
                    frm.refresh_field("start_date");
            frm.set_value("end_date",    period.end_date);
                    frm.refresh_field("end_date");
            frm.set_value("total_days", period.total_days);
                    frm.refresh_field("total_days");
        });
        frm.refresh_field("customer");
    },
    contract:function(frm){
        frappe.model.clear_table(frm.doc, "attendance_details");
        frm.refresh_field("attendance_details");
        cur_frm.fields_dict.contract.get_query = function(doc) {
            return {
                filters: { "party_name" : cur_frm.doc.customer, "docstatus" : 1, "status" : "Active" }
            }
        }
        frm.refresh_field("site");
        frm.refresh_field("site_name");
    },
    get_posting_details:function(frm){
        frm.refresh_field("name");
        if(frm.doc.attendance_period != undefined && frm.doc.customer != undefined && frm.doc.contract != undefined){
            frappe.call({
                method:"get_posting_details",
                doc: cur_frm.doc,
                callback:function(data){
                    if (data.message){
                        frappe.model.clear_table(frm.doc, "attendance_details");
                        frm.refresh_field("attendance_details");
                        $.each(data.message || [], function(index, row) {
                            var doc_emp_details = frappe.model.add_child(frm.doc, "Attendance Details", "attendance_details");
                            doc_emp_details.employee=           row.employee;
                            doc_emp_details.employee_name=      row.employee_name;
                            doc_emp_details.work_type= 		    row.work_type;
                            doc_emp_details.wage_rule= 		    row.wage_rule;
                            doc_emp_details.present_duty= 	    row.pd;
                            doc_emp_details.week_off= 		    row.wo;
                            doc_emp_details.extra_duty= 	    row.ed;
                            doc_emp_details.national_holidays= 	row.nh;
                        });
                        frm.refresh_field("attendance_details");
                    }
                }
            })
        }else{
            frappe.model.clear_table(frm.doc, "attendance_details");
		    frm.refresh_field("attendance_details");
		    return false
        }
	    cur_frm.set_value('last_synced', frappe.datetime.now_datetime());
        frm.refresh_field('last_synced');
    },
    on_submit : function(frm){
        cur_frm.set_df_property("attendance_period", "reqd", true);
        cur_frm.set_df_property("get_posting_details", "hidden", true);
    },
    before_submit: function(frm){
	    if(frm.doc.attendance_details.length < 1){
            frappe.msgprint("Employee Attendance Details Not Present")
            frappe.validated = false;
        }
    },
	before_save: function(frm){
		if(frm.doc.attendance_details && frm.doc.attendance_details.length > 0){
			var total_pd= 0.0
        	var total_wo= 0.0
        	var total_ed= 0.0
        	var total_nh= 0.0
			for(var i= 0; i < frm.doc.attendance_details.length; i++){
				if (frm.doc.attendance_details[i].national_holidays > 2){
					frappe.throw(`NH should be (0 or 1 or 2 at row postion ${i+1})`)
				}					
                total_pd= total_pd + frm.doc.attendance_details[i].present_duty
                total_wo= total_wo + frm.doc.attendance_details[i].week_off
                total_ed= total_ed + frm.doc.attendance_details[i].extra_duty
                total_nh= total_nh + frm.doc.attendance_details[i].national_holidays
			}
			frm.set_value('total_pd', total_pd)
       		frm.refresh_field("total_pd");
			frm.set_value('total_wo', total_wo)
       		frm.refresh_field("total_wo");
			frm.set_value('total_ed', total_ed * 2)
       		frm.refresh_field("total_ed");
        	total_nh= total_nh
			frm.set_value('total_nh', total_nh)
       		frm.refresh_field("total_nh");
			frm.set_value('total_pd_ed', total_pd + total_ed)
       		frm.refresh_field("total_pd_ed");
			frm.set_value('total_pd_ed_wo', total_pd + total_ed + total_wo)
       		frm.refresh_field("total_pd_ed_wo");
			frappe.call({
				method: "frappe.client.get",
				args: {"doctype": "Contract", "name": frm.doc.contract},
				callback:function(r){
					if(r.message){
						var contract= r.message
						var total_quantity= 0
						var att_threshold= 0
						var att_length= frm.doc.attendance_details.length
						var period_days= frappe.datetime.get_day_diff(frm.doc.end_date , frm.doc.start_date) + 1
						var start_date= new Date(frm.doc.start_date)
						var end_date= new Date(frm.doc.end_date)
						var total_sunday= 0
						for (var i = start_date; i <= end_date; ){
						    if (i.getDay() == 0){
							        total_sunday++;
    						}
							i.setTime(i.getTime() + 1000*60*60*24);
							console.log(i)
						}
						for(var i= 0; i < contract.contract_details.length; i++){
							total_quantity= total_quantity + contract.contract_details[i].quantity
						}
						if(att_length < total_quantity){
							if (frm.doc.weekly_off_included == 0){
								 att_threshold = ((att_length * period_days) + (att_length))
							}else{
								 att_threshold = ((att_length * period_days) + (total_sunday * att_length) + (att_length))	
							}
						}
						else{
							if (frm.doc.weekly_off_included == 0){
								att_threshold = ((total_quantity * period_days) + (total_quantity))
                            }else{
								att_threshold = ((total_quantity * period_days) + (total_sunday * total_quantity) + (total_quantity))
                            }
						}
						if(frm.doc.total_pd_ed_wo + total_nh > att_threshold){
							frappe.msgprint("Attendance Exceeded !! Please enter reason in remark field")
							cur_frm.set_df_property("remark", "hidden", false);
							cur_frm.set_df_property("remark", "reqd", true);		
						}
						else{
							frm.set_value('remark', "")
				            frm.refresh_field("remark");
							cur_frm.set_df_property("remark", "hidden", true);        
                            cur_frm.set_df_property("remark", "reqd", false);
						}
					}
				}
			});
		}
	}
    /*validate: function(frm){
        *//*if (frm.doc.attendance_details != undefined){
            if(cur_frm.doc.attendance_details.length > 0){
                frappe.model.with_doc("Contract", cur_frm.doc.contract, function() {
                    var contract = frappe.model.get_doc("Contract", cur_frm.doc.contract);
                    var validated= false;
                    $.each(cur_frm.doc.attendance_details, function(index, row){
                        // Calculate Bill Duty based on W/O included Yes/No in Contract
                        if(contract.is_weekly_off_included){
                            row.bill_duty= flt(row.present_duty + row.week_off + row.extra_duty);
                        }else{
                            row.bill_duty= flt(row.present_duty + (row.extra_duty * 2));
                        }
                        row.present_duty = 4;
                        if(flt(row.present_duty) > 1){
                            // Get Wage Hrs & Contract Hrs for calculate Payroll Duty
                            frappe.model.with_doc("Salary Structure", row.wage_rule, function() {
                                var salary_struct = frappe.model.get_doc("Salary Structure", row.wage_rule);
                                var count= 0;
                                var payroll_duty=0.00;

                                console.log("### Row: "+index+"### Salary Structure ####",salary_struct);
                                if(salary_struct.docstatus == 1 && salary_struct.is_active == "Yes"){
                                    var period_start_dt = new Date(cur_frm.doc.start_date); // Attendance Period Start Date
                                    var period_end_dt = new Date(cur_frm.doc.end_date); // Attendance Period End Date

                                    $.each(salary_struct.wage_rule_details, function(index2, new_row){
                                        var wage_rv_frmdt = new Date(new_row.from_date); // Wage Rule Details Revision Fron Date
                                        var wage_rv_todt = new Date(new_row.to_date); // Wage Rule Details Revision To Date

                                        if(wage_rv_frmdt <= period_start_dt && wage_rv_todt >= period_end_dt){
                                            count++;
                                            if(count == 1){
                                                if(new_row.wage_hours > 0){
                                                    var calc_pd= flt((row.present_duty * new_row.contract_hours) / new_row.wage_hours);
                                                    var calc_ed= flt((row.extra_duty * new_row.contract_hours) / new_row.wage_hours);
                                                    //console.log("##"+index+":::CHrs:"+new_row.contract_hours+":::WHrs:"+new_row.wage_hours+"::::PD + WO + ED + CPD + CED::"+flt(row.present_duty)+"+"+flt(row.week_off) +"+"+flt(row.extra_duty)+"+"+calc_pd+"+"+calc_ed)
                                                    payroll_duty= flt(flt(row.present_duty) + flt(row.week_off) + flt(row.extra_duty) + calc_pd + calc_ed);
                                                    row.payroll_duty = payroll_duty;
                                                    validated= true;
                                                }else{
                                                    frappe.throw("Wage Hours should be greater than zero in Wage Rule : {0}",[new_row.name])
                                                    validated= false;
                                                }
                                            }
                                        }
                                        return validated
                                    });
                                    if(count > 1){
                                        frappe.throw({
                                            title: __('Salary Structure'),
                                            message: __("Salary Structure '{0}' Multiple Revisions found in between period '{1} - {2}' ",[row.wage_rule,moment(period_start_dt).format('DD-MM-YYYY'),moment(period_end_dt).format('DD-MM-YYYY')]),
                                            indicator: 'red'
                                        });
                                        validated= false;
                                    }
                                    if(count == 0){
                                        frappe.throw({
                                            title: __('Salary Structure'),
                                            message: __("Salary Structure : {0}. Revision not found in period '{1} - {2}' ",[row.wage_rule,moment(period_start_dt).format('DD-MM-YYYY'),moment(period_end_dt).format('DD-MM-YYYY')]),
                                            indicator: 'red'
                                        });
                                        validated= false;
                                    }
                                    console.log("### Count :::::::::::: ",count);
                                }else{
                                    frappe.throw(__("Salary Structure : {0} should be submitted and active",[row.wage_rule]))
                                    validated= false;
                                }
                            });
                        }else{
                            frappe.msgprint(__("Present Duty(PD) should be greater than zero. "));
                            validated= false;
                        }
                        return validated;
                    });
                });
            }
        }*//*
	
    },*/
});

