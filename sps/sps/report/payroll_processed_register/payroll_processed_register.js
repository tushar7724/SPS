// Copyright (c) 2016, TUSHAR TAJNE and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Payroll Processed Register"] = {
	"filters": [
	    {
			"fieldname":"period",
			"label": __("Payroll Period"),
			"fieldtype": "Link",
			"options": "Payroll Period",
			"default":moment(frappe.datetime.nowdate()).format('MMMYYYY'),
			"reqd": 1
		},
		/*{
			"fieldname":"start_date",
			"label": __("From"),
			"fieldtype": "Date",
			"default": frappe.datetime.add_months(frappe.datetime.get_today(),-1),
			"fetch_from": "period.start_date",
			"reqd": 1
		},
		{
			"fieldname":"end_date",
			"label": __("To"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"fetch_from": "period.end_date",
			"reqd": 1
		},*/
		{
			"fieldname":"employee",
			"label": __("Employee"),
			"fieldtype": "Link",
			"options": "Employee"
		},
		{
			"fieldname":"company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company")
		},
		{
			"fieldname":"docstatus",
			"label":__("Document Status"),
			"fieldtype":"Select",
			"options":["Draft", "Submitted", "Cancelled"],
			"default":"Submitted"
		}
	]
}