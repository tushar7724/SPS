# -*- coding: utf-8 -*-
# Copyright (c) 2018, TUSHAR TAJNE and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import cint, flt, add_months, today, date_diff, getdate, add_days, cstr, nowdate
from frappe.model.document import Document
from frappe import _

class SPSAttendance(Document):
	def validate(self):

		if self.docstatus == 0:
			frappe.db.set(self, 'status', 'Draft')
		self.attendance_name = str(self.attendance_period) + "-" + str(self.contract)

		if self.site:
			contract= frappe.get_doc("Contract", self.contract)
			if contract.bu_site  != self.site:
				frappe.throw("Site: {0} Is Invalid For Contract : {1}".format(self.site, self.contract))
			else: pass

		if not self.start_date:
			frappe.throw("Start-Date can not be empty")
		else:
			period= frappe.get_doc("Payroll Period", self.attendance_period)
			if str(period.start_date) !=  str(self.start_date):
				frappe.throw("Start-Date should be equal to period FromDate.")
			else: pass

		if not self.end_date:
			frappe.throw("End Date Can Not Empty")
		else:
			period= frappe.get_doc("Payroll Period", self.attendance_period)
			if str(period.end_date) != str(self.end_date):
				frappe.throw("End-Date should be equla to period ToDate.")
			else: pass

		if self.attendance_details:
			for d in self.attendance_details:
				if not d.employee_name:
					frappe.throw("Employee not exist")

		self.posting_validation()
		self.validate_structure()

	def on_update(self):
		pass

	def	posting_validation(self):
		data= self.get_emp_for_print_format()
		emp_wr = {}
		employees= []
		emp_wt= []
		emp_wt2= []

		if len(data) < 1:
			frappe.throw("Posting Details Is Not Available For Contract %s" %(self.contract))
		else:
			for i in range(0, len(data)):
				employees.append(data[i]["employee"])
				emp_wt.append(str(data[i]["employee"]) + str(data[i]["work_type"]))
				emp_wr[str(data[i]["employee"]) + str(data[i]["work_type"])] = data[i]["wage_rule"]

			for i in self.attendance_details:

				emp_wt2.append(str(str(i.employee) + str(i.work_type)))
				if i.employee not in employees:
					frappe.throw("Employee : {0} posting not avalable".format(i.employee))
				if (str(i.employee) + str(i.work_type)) not in emp_wt:
					frappe.throw("Employee: %s not posted on Work Type: %s" %(i.employee, i.work_type))

				if (str(i.employee) + str(i.work_type)) in emp_wr:
					i.wage_rule = str(emp_wr[str(i.employee) + str(i.work_type)])
				else: frappe.throw("Wage Rule Not linked for Employee: %s ::: Work Type: %s" % (i.employee, i.work_type))

			k=set([x for x in emp_wt2 if emp_wt2.count(x) > 1])
			if k:
				frappe.throw("Multiple times posting for same Employee on Same work Type : %s" %k)

	def on_submit(self):
		if self.site_name == "":
			frappe.throw("Site Name Can Not Be Empty")
		frappe.db.set(self, 'status', 'To Bill')

	def on_cancel(self):
		frappe.db.set(self, 'status', 'Cancelled')

	def before_save(self):
		self.branch=None
		if self.customer:
			customer_code = frappe.db.get_value("Customer", self.customer, "customer_code")
			if customer_code:
				self.branch = frappe.db.get_value("Business Unit", customer_code, "business_unit")
			else: frappe.throw(_("Customer not exist in Business Unit"))
		total_pd= 0.0
		total_wo= 0.0
 		total_ed= 0.0
		total_nh= 0.0
		if len(self.attendance_details) > 0:
			for emp_att in range(0, len(self.attendance_details)):
				total_pd= total_pd+ float(self.attendance_details[emp_att].present_duty)
				total_wo= total_wo+ float(self.attendance_details[emp_att].week_off)
				total_ed= total_ed+ float(self.attendance_details[emp_att].extra_duty)
				total_nh= total_nh+ float(self.attendance_details[emp_att].national_holidays)
		self.total_pd= total_pd
		self.total_wo= total_wo
		self.total_ed= total_ed * 2
		self.total_nh= total_nh
		self.total_pd_ed= float(self.total_pd+ self.total_ed)
		self.total_pd_ed_wo= float(self.total_pd + self.total_ed + self.total_wo)

	def validate_structure(self):
		if self.attendance_details or len(self.attendance_details) > 0:
			is_wo_included = frappe.db.get_value("Contract", self.contract, 'is_weekly_off_included')
			for att_row in self.get("attendance_details"):
				if not att_row.present_duty:att_row.present_duty=0
				if not att_row.extra_duty:att_row.extra_duty=0
				if not att_row.week_off:att_row.week_off=0
				if not att_row.national_holidays:att_row.national_holidays=0
				if att_row.national_holidays > 2: frappe.throw("NH Should be (0 or 1 or 2) at row postion %s" %(att_row.idx))
				total = att_row.present_duty + att_row.week_off + att_row.extra_duty + att_row.national_holidays
				if not (total > 0): frappe.throw(_("PD / WO / ED / NH should be greater than zero."))

				if is_wo_included:
					att_row.bill_duty = float(float(att_row.present_duty) + float(att_row.week_off) + float(att_row.extra_duty))
				else : att_row.bill_duty= float(float(att_row.present_duty) + (float(att_row.extra_duty) * 2))

				if att_row.wage_rule:
					salary_structure = frappe.get_doc("Salary Structure", att_row.wage_rule)
					if (salary_structure.docstatus == 1 and salary_structure.is_active == "Yes"):
						period_start_dt = getdate(self.start_date)  # Attendance Period Start Date
						period_end_dt = getdate(self.end_date)  # Attendance Period End Date
						count= 0
						if salary_structure.wage_rule_details:
							for wr in salary_structure.wage_rule_details:
								wage_rv_frmdt = getdate(wr.from_date)  # Wage Rule Details Revision From Date
								wage_rv_todt = getdate(wr.to_date)  # Wage Rule Details Revision To Date
								if (wage_rv_frmdt <= period_start_dt and wage_rv_todt >= period_end_dt):
									count=count+1
									if count > 1: frappe.throw(_("Salary Structure : '{0}', Multiple Wage Rule Revisions found between '{1} - {2}' ").format(att_row.wage_rule,period_start_dt,period_end_dt))
									if count == 1:
										if (wr.wage_hours > 0 and wr.contract_hours > 0 ):
											calc_pd = flt((att_row.present_duty * wr.contract_hours) / wr.wage_hours)
											calc_ed = flt((att_row.extra_duty * wr.contract_hours) / wr.wage_hours)
											att_row.payroll_duty = flt(flt(att_row.week_off) + calc_pd + calc_ed)
											att_row.wage_rule_details = wr.name
											att_row.wage_rule_revision = wr.revision
										else: frappe.throw(_("Row# {0} : Wage Hours and Contract Hours should be greater than zero").format(att_row.idx))
									pass
								pass
							if count == 0: frappe.throw(_("Salary Structure '{0}'. Wage Rule not found between '{1} - {2}' ").format(att_row.wage_rule, period_start_dt, period_end_dt))
						else: frappe.throw(_("Wage Rule Detail Not found in Salary Structure: {0}").format(att_row.wage_rule))
					else: frappe.throw(_("Salary Structure: {0} should be Active").format(att_row.wage_rule))
				pass
			pass
		pass

	def get_posting_details(self):
		import datetime
		result = []
		contract_data = frappe.db.sql(""" SELECT DISTINCT employee,employee_name, work_type, wage_rule FROM `tabPeople Posting`
						INNER JOIN my_date_series ON ( dateval >= from_date and dateval <= to_date )
						WHERE dateval >= '%s' and dateval <= '%s'
						AND parent= '%s' AND employee IS NOT NULL AND employee != "" AND employee != 'S000000'
						order by work_type, employee, dateval"""
									  % (str(self.start_date), str(self.end_date), self.contract))
		contract_data_in_dic = []
		for i in range(0, len(contract_data)):
			dic = {}
			dic["employee"] = contract_data[i][0]
			dic["employee_name"] = contract_data[i][1]
			dic["work_type"] = contract_data[i][2]
			dic["wage_rule"] = contract_data[i][3]
			contract_data_in_dic.append(dic)
		patt = []
		for idx, d in enumerate(contract_data_in_dic):
			patt.append({"employee": d["employee"],"employee_name": d["employee_name"], "work_type": d["work_type"], "wage_rule": d["wage_rule"], "pd": 0,
						 "wo": 0, "ed": 0, "nh": 0, })
		for i in range(0, len(self.attendance_details)):
			a= self.attendance_details[i].as_dict()
			for j, pat in enumerate(patt):
				if a["employee"] == pat["employee"] and a["work_type"] == pat["work_type"]:
					pat["pd"] = a["present_duty"]
					pat["wo"] = a["week_off"]
					pat["ed"] = a["extra_duty"]
					pat["nh"] = a["national_holidays"]
		result = patt
		return result

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
		

	def get_emp_for_print_format(self):
		data= frappe.db.sql(""" SELECT DISTINCT employee,employee_name, work_type, wage_rule, from_date, to_date FROM `tabPeople Posting`
                         INNER JOIN my_date_series ON ( dateval >= from_date and dateval <= to_date )
                         WHERE dateval >= '%s' and dateval <= '%s'
                         AND parent= '%s' AND employee IS NOT NULL AND employee != ""
						 order by work_type, employee, dateval"""
                         % (str(self.start_date), str(self.end_date), self.contract), as_dict= True)
		return data
		
