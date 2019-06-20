// Copyright (c) 2016, TUSHAR TAJNE and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["SPS Attendance Report"] = {
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
            "label": __("Period"),
            "fieldtype": "Link",
            "options": "Payroll Period",
            "reqd": 1
        },
        {
            "fieldname":"customer",
            "label": __("Customer"),
            "fieldtype": "Link",
            "options": "Customer",
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
        },
        {
            "fieldname":"status",
            "label": __("Attendance Status"),
            "fieldtype": "Select",
            "options": "\nDraft\nCompleted\nCancelled\nTo Bill"
        },
        {
            "fieldname":"employee",
            "label": __("Employee"),
            "fieldtype": "Link",
            "options": "Employee"
        },
        {
            "fieldname":"work_type",
            "label": __("Work Type"),
            "fieldtype": "Link",
            "options": "Work Type"
        },
        {
            "fieldname":"docstatus",
            "label": __("Document Status"),
            "fieldtype": "Select",
            "default":"Submitted",
            "options":["Draft", "Submitted", "Cancelled"],
        }
    ]
}
