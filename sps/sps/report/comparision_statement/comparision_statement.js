// Copyright (c) 2016, TUSHAR TAJNE and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Comparision Statement"] = {
	"filters": [
	    {
			"fieldname":"company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company"),
			"reqd": 1
		},
	    {
			"fieldname":"period",
			"label": __("Payroll Period"),
			"fieldtype": "Link",
			"options": "Payroll Period",
			"default":"May2019",
			//"default":moment(frappe.datetime.nowdate()).format('MMMYYYY')+"-A",
			"reqd": 0
		},
		{
			"fieldname":"type",
			"label": __("Type"),
			"fieldtype": "Select",
			"options": "All\nAttendance Zero\nTo Bill",
			"default":"All"
		},
		{
			"fieldname":"customer",
			"label": __("Customer"),
			"fieldtype": "Link",
			"options": "Customer"
		},
		{
			"fieldname":"site",
			"label": __("Site"),
			"fieldtype": "Link",
			"options": "Business Unit"
		},
		{
			"fieldname":"contract",
			"label": __("Contract"),
			"fieldtype": "Link",
			"options": "Contract"
		}
	]
}
