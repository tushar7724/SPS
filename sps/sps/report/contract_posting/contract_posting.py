# Copyright (c) 2013, TUSHAR TAJNE and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
	columns, data = [], []
	if len(filters.keys()) > 1:
		rows= []
		if not filters:
			columns, data = [], []
		if filters and filters != None:
			conditions, period = get_conditions(filters)
			rows= get_data(filters, conditions, period)
		columns=[   _("Company") + ":Link/Company:220",
                    _("Customer") + ":Link/Customer:220",
                    _("Site") + ":Link/Business Unit:220",
                    _("Site Name") + ":Data:220",
                    _("Contract") + ":Link/Contract:220",
					_("Start Date") + ":Date:80",
					_("End Date") + ":Date:80",
					_("Posting Required") + ":Int:80",	
					_("Posting Count") + ":Int:80",	
					_("Posting Sortage") + ":Int:80",
					_("Reliever Required") + ":Int:80",
					_("Reliever Count")	+ ":Int:80",
					_("Reliever Sortage") + ":Int:80"
                ]	
		if len(rows) > 0:
			for i in rows:
				row= [i.company, i.party_name, i.bu_site, i.bu_site_name, i.parent, i.start_date, i.end_date, i.require_quantity, i.posted_quantity, i.posting_sortage, i.reliever_quantity, i.reliever_posted_quantity , i.reliever_sortage]
				data.append(row)
	return columns, data

def get_conditions(filters):
	conditions= ""
	period= frappe.get_doc("Payroll Period", filters.get('period'))
	if filters.get("company"):  conditions+=  "company = '%s' " %(filters.get('company'))
	if filters.get("period"):   conditions+=  " and dateval >= '%s' and dateval <= '%s' " %(period.start_date, period.end_date)
	if filters.get("customer"): conditions+=  " and party_name= '%s' "%(filters.get('customer'))
	if filters.get("site"):     conditions+=  " and bu_site = '%s' "%(filters.get('site'))
	return conditions, period

def get_data(filters, conditions, period):
	data= frappe.db.sql("""	select distinct pp.parent, con.party_name, con.bu_site, con.bu_site_name,
							con.start_date, con.end_date, con.company from `tabPeople Posting` pp
							INNER JOIN my_date_series ON ( dateval >= pp.from_date and dateval <= pp.to_date )
							INNER JOIN `tabContract` con ON con.name= pp.parent
							WHERE %s and (pp.employee IS NULL or pp.employee = "")
						""" %(conditions), as_dict= 1)
	for i in range(0, len(data)):
		temp= frappe.db.sql("""select sum(quantity), sum(CEIL(quantity/6)) from `tabContract Details` where parent= '%s'""" %(data[i]["parent"]))
		temp2= frappe.db.sql("""select name from `tabPeople Posting`
                                INNER JOIN my_date_series ON (dateval >= from_date and dateval <= to_date)
                                where parent = '%s' and posting_type= 'Normal' and (employee IS NULL or employee = "")
                                and dateval >= '%s' and dateval <= '%s' group by srno,work_type """ %(data[i]["parent"], period.start_date, period.end_date), as_dict= 1)
		temp3= frappe.db.sql("""select name from `tabPeople Posting`
                                INNER JOIN my_date_series ON (dateval >= from_date and dateval <= to_date )
                                where parent = '%s' and posting_type= 'Reliever' and (employee IS NULL or employee = "")
                                and dateval >= '%s' and dateval <= '%s' group by srno""" %(data[i]["parent"], period.start_date, period.end_date), as_dict= 1)
		data[i]["require_quantity"]=  int(temp[0][0] if temp[0][0] is not None else 0)
		data[i]["reliever_quantity"]= int(temp[0][1] if temp[0][1] is not None else 0)
		data[i]["posted_quantity"]= int(temp[0][0] if temp[0][0] is not None else 0) - len(temp2)
		data[i]["reliever_posted_quantity"]= int(temp[0][1] if temp[0][1] is not None else 0) - len(temp3)
		data[i]["posting_sortage"]=  len(temp2)
		data[i]["reliever_sortage"]= len(temp3)
	return data


