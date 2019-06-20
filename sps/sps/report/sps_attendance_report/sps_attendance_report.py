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
			conditions= get_conditions(filters)[0]
			rows= get_data(filters, conditions)
		columns=[   _("Company") + ":Link/Company:220",
					_("Period")  + ":Link/Payroll Period:220",
					_("Customer") + ":Link/Customer:220",
					_("Site") + ":Link/Business Unit:220",
					_("Contract") + ":Link/Contract:220",
					_("Attendance") + ":Link/SPS Attendance:220", 
					_("Employee") + ":Link/Employee:220",
					_("Work Type") + ":Link/Work Type:220",
					_("PD") + ":Float:50",
					_("WO") + ":Float:50",
					_("ED") + ":Float:50",
					_("NH") + ":Float:50",
					_("Total (PD+ED)") + ":Float:80",
					_("Total (PD+ED+WO)") + ":Float:80",
					_("Status") + ":Data:120"
				]
		if rows and len(rows) > 0:
			for i in rows:
				row= [	i.company, i.attendance_period, i.customer, i.site, i.contract, i.attendance_name,
						i.employee, i.work_type, i.present_duty, i.week_off, i.extra_duty, i.national_holidays,
						i.present_duty + i.extra_duty, i.present_duty + i.extra_duty + i.week_off, i.status
					 ]
				data.append(row)
	else: columns, data = [], []
	return columns, data

def get_data(filters, conditions):
	data= frappe.db.sql(""" Select sat.company, sat.attendance_period, sat.customer, sat.site, sat.contract, sat.attendance_name, sat.status,
						 	atd.employee, atd.work_type, atd.present_duty, atd.week_off, atd.extra_duty, atd.national_holidays
							From `tabSPS Attendance` sat Inner Join `tabAttendance Details` atd On atd.parent = sat.name 
							Where %s""" %(conditions), as_dict=1)
	return data

def get_conditions(filters):
	conditions= ""
	docstatus = {"Draft": 0, "Submitted": 1, "Cancelled": 2}
	if filters.get("company"):conditions+= "sat.company = '%s'" %(filters.get('company'))
	if filters.get("period"):conditions+= " and sat.attendance_period = '%s'" %(filters.get('period'))
	if filters.get("customer"):conditions+= " and sat.customer = '%s'" %(filters.get('customer'))
	if filters.get("site"): conditions+= " and sat.site = '%s'" %(filters.get('site'))
	if filters.get("contract"): conditions+= " and sat.contract = '%s'" %(filters.get('contract'))
	if filters.get("status"): conditions+= " and sat.status = '%s'" %(filters.get('status'))
	if filters.get("employee"): conditions+= " and atd.employee = '%s'" %(filters.get('employee'))
	if filters.get("work_type"): conditions+= " and atd.work_type = '%s'" %(filters.get('work_type'))
	if filters.get("docstatus"): conditions+= " and sat.docstatus = %s" %(docstatus[filters.get('docstatus')])
	return conditions, filters 
