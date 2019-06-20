# -*- coding: utf-8 -*-
# Copyright (c) 2019, TUSHAR TAJNE and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import cint, flt, add_months, today, date_diff, getdate, add_days, cstr, nowdate
class AttendancePrint(Document):
	def get_period_date_days(self):
		from datetime import date, timedelta
		d1= getdate(self.start_date)
		d2= getdate(self.end_date)
		delta = d2 - d1         # timedelta
		dates_days= []
		for i in range(delta.days + 1):
			x= (d1 + timedelta(i))
			x= str(x).split("-")
			dates_days.append(x[2])
		return dates_days

	def get_contracts(self):

		conditions = ""
		if self.customer: conditions += " and party_name = '%s'" % (self.customer)
		if self.site: conditions += " and bu_site = '%s'" % (self.site)
		if self.contract: conditions += " and name = '%s'" % (self.contract)

		period_doc = frappe.get_doc('Payroll Period', self.period)

		contract = frappe.db.sql(
			""" select * from`tabContract`
			where start_date <= '%s'
			and end_date => '%s'
			and docstatus=1 %s """,
			(getdate(period_doc.end_date),getdate(period_doc.start_date),conditions), as_dict=1)
		return contract or {}

	def get_emp_for_print_format(self):
		conditions= self.get_conditions()
		contracts= []
		extra_info= []

		data= frappe.db.sql("""
							SELECT DISTINCT @row_number:=CASE WHEN @customer_no = tpp.parent THEN @row_number + 1 ELSE 1 END AS ronum, 
							@customer_no:=tpp.parent , tpp.work_type, tpp.employee, tpp.employee_name, 
							tpp.wage_rule, tpp.from_date, tpp.to_date, tpp.parent, tc.party_name, tc.bu_site_name, tc.bu_site, tc.company
							FROM `tabPeople Posting` as tpp
							INNER JOIN my_date_series as mds ON ( mds.dateval >= tpp.from_date and mds.dateval <= tpp.to_date)
							INNER JOIN `tabContract` as tc ON tc.name = tpp.parent AND tc.docstatus = 1 AND tc.status= 'Active'
							WHERE mds.dateval >= '%s' 
							AND mds.dateval <= '%s' 
							AND tpp.employee IS NOT NULL AND tpp.employee != ""  %s
							ORDER BY tpp.parent, tpp.work_type, tpp.employee, ronum, mds.dateval; 
							""" 
						 % (str(self.start_date), str(self.end_date), conditions), as_dict= True)
		print data
		for i in range(0, len(data)):
			if data[i]["parent"] not in contracts:
				temp= {}
				temp["site"]= data[i]["bu_site"]
				temp["site_name"]= data[i]["bu_site_name"]
				temp["contract"]= data[i]["parent"]
				temp["customer"]= data[i]["party_name"]
				extra_info.append(temp)
				contracts.append(data[i]["parent"])
		for i in range(0, len(data)):
			print data[i]["ronum"], data[i]["parent"]
		return data, extra_info 
	
	def get_conditions(self):
		conditions= ""
		if self.customer: conditions+= " and tc.party_name = '%s'" %(self.customer)
		if self.site: conditions+= " and tc.bu_site = '%s'" %(self.site)
		if self.contract: conditions+= " and tpp.parent = '%s'" %(self.contract)
		return conditions
