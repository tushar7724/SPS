# -*- coding: utf-8 -*-
# Copyright (c) 2019, TUSHAR TAJNE and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import cint, flt, add_months, today, date_diff, getdate, add_days, cstr, nowdate
from frappe.model.document import Document

class AttendanceSheet(Document):
	def get_period_date_days(self):
		from datetime import date, timedelta
		d1 = getdate(self.start_date)
		d2 = getdate(self.end_date)
		delta = d2 - d1  # timedelta
		dates_days = []
		for i in range(delta.days + 1):
			x = (d1 + timedelta(i))
			x = str(x).split("-")
			dates_days.append(x[2])
		return dates_days

	def get_contracts(self):
		period_doc = frappe.get_doc('Payroll Period', self.period)
		conditions = " and tc.start_date <= '%s' and tc.end_date >= '%s'" %(str(period_doc.end_date), str(period_doc.start_date))
		if self.customer: conditions +=" and tc.party_name = '%s'" % (self.customer)
		if self.site: conditions +=" and tc.bu_site = '%s'" % (self.site)
		if self.contract: conditions +=" and tc.name = '%s'" % (self.contract)
		if self.branch_manager: conditions += " and tbu.branch_manager= '%s'" %(self.branch_manager)
		if self.area_officer: conditions += " and tbu.area_officer= '%s'" %(self.area_officer)
		#contract = frappe.db.sql("""select distinct name,contract_name,party_name,bu_site_name from`tabContract` where docstatus=1 %s ORDER BY contract_name""" %(conditions),as_dict=1)
		contract= frappe.db.sql("""
									select distinct tc.name, tc.contract_name, tc.party_name, tc.bu_site_name
									from`tabContract` tc
									Inner join `tabBusiness Unit` tbu on tbu.name= tc.bu_site
									where tc.docstatus=1 and tc.status= 'Active' %s ORDER BY tc.contract_name;
								"""%(conditions),as_dict=1)
		data={}
		if contract:
			for c in contract:
				pd = frappe.db.sql(
					"""select parent,employee,employee_name,work_type,from_date,to_date from`tabPeople Posting` where employee !="" and parent='%s' and docstatus=1 """ % (c.name), as_dict=1)
				if pd:
					for idx,pdd in enumerate(pd):
						pdd['contract_id']=c.name
						pdd['contract_name']=c.contract_name
						pdd['party_name']=c.party_name
						pdd['bu_site_name']=c.bu_site_name
					if c.name in data: data[c.name]+= pd
					else:data[c.name]= pd
		print"######### Total No.of Attendance Sheet( Contracts ): %s ############" % len(data)
		return data or {}
