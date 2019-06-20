# -*- coding: utf-8 -*-
# Copyright (c) 2019, TUSHAR TAJNE and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe import utils
from frappe.utils import getdate

class SalaryPayout(Document):
	def before_cancel(self):
		if self.pay_slip_status == 'Paid' and getdate(self.creation) != getdate(frappe.utils.nowdate()):
			frappe.throw("Doc can not be cancel")
		else:
			data= frappe.get_list('Processed Payroll', fields=['name'], filters=[['payment_batch', '=', self.name]])
			for i in range(0, len(data)):
				doc= frappe.get_doc('Processed Payroll', data[i]["name"])
				doc.pay_slip_status= 'Prepared'
				doc.submit()
				doc.reload()

	def on_submit(self):
		self.pay_out()
	
	def pay_out(self):
		total_payout_amount= 0.0
		count= 0
		pay_details= self.get_employee_list()
		if len(pay_details) > 0:
			for emp in range(0, len(pay_details)):
				emp_status= frappe.get_list('Employee', fields=['status', 'bank_name', 'bank_ifsc_code', 'bank_ac_no', 'relieving_date'], filters=[['name', '=', str(pay_details[emp]['emp_id'])]])
				if emp_status[0]['status'].upper() == 'ACTIVE' or (emp_status[0]['status'].upper() == 'RESIGNED' and (getdate(self.from_date) <= getdate(emp_status[0]['relieving_date']) <= getdate(self.to_date))):
					ispayout= True
					if self.bank != None and self.bank != '' and self.bank != emp_status[0]['bank_name']:
						ispayout= False
					if ispayout == True:
						count= count + 1
						total_payout_amount= total_payout_amount + float(pay_details[emp]['net_pay'])
						doc= frappe.get_doc('Processed Payroll', str(pay_details[emp]['name']))
						doc.pay_slip_status= self.pay_slip_status
						doc.payment_batch= self.name
						doc.paid_on= utils.today()
						doc.pay_mode= self.pay_mode
						doc.paid_by= frappe.session.user
						doc.bank_name= emp_status[0]['bank_name']
						doc.bank_ac_no= emp_status[0]['bank_ac_no']
						doc.bank_ifsc_code= emp_status[0]['bank_ifsc_code']
						doc.remark=  self.remark
						doc.submit()
						doc.reload()
			frappe.db.set_value("Salary Payout", self.name, "total_pay_amount", total_payout_amount, update_modified=True)
			frappe.db.set_value("Salary Payout", self.name, "number_of_employee", count, update_modified= True)
			self.reload()
			frappe.msgprint("Payout Process Successfully Done!!")
		else: frappe.throw("No Data Found For Payout Process")
	
	def get_employee_list(self):
		myfilters= [['docstatus', '=', 1], ['period', '=', self.period], ['pay_slip_status', '=', 'Prepared']]
		if self.location != "" and self.location != None:
			myfilters.append(['location', '=', self.location])
		if self.customer != "" and self.customer != None:
			myfilters.append(['customer', '=', self.customer])
		pay_details= frappe.get_list('Processed Payroll', order_by='site', fields=['name', 'emp_id', 'net_pay'], filters= myfilters, limit= self.number_of_employee if self.number_of_employee != None and self.number_of_employee > 0 else 500)
		return pay_details
	def print_format(self):
		data= frappe.get_all('Processed Payroll', order_by='site', filters= [['pay_slip_status', '=', 'Paid'], ['payment_batch', '=', self.name]], fields=['net_pay', 'emp_id', 'emp_name', 'company', 'customer', 'bank', 'bank_ac_no', 'bank_ifsc_code'])
		return data
		
	
