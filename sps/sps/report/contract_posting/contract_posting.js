// Copyright (c) 2016, TUSHAR TAJNE and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Contract Posting"] = {
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
						"reqd" : 1
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
                    }

	]
}
