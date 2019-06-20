# -*- coding: utf-8 -*-
# Copyright (c) 2018, TUSHAR TAJNE and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import nowdate, getdate, get_datetime
import calendar
from frappe.model.mapper import get_mapped_doc
import math
from frappe.utils import flt, cint
from frappe.model.document import Document

class WageRule(Document):

	def __init__(self, *args, **kwargs):
		super(WageRule, self).__init__(*args, **kwargs)

	def validate(self):
		#rule_code = frappe.db.get_value("Wage Rule", {"rule_code": self.rule_code},"rule_code")
		#if self.is_new() and self.amended_from:
			#self.revision_number = self.revision_number + 1

		self.validate_prevdoc_dates()
		#if self.is_new() and self.amended_from != None and self.revision_number==1:
			#frappe.throw(_("Rule Code '{0}' Already Exist with Revision Number '{1}'").format(self.rule_code, self.revision_number))

		if self.party_name and self.rule_code and self.revision_number:
			wr = frappe.db.sql("select rule_code from `tabWage Rule` \
						where  party_name = %s and revision_number = %s and docstatus = 1\
						and rule_code = %s", (self.party_name, self.revision_number, self.rule_code))
			if wr and wr[0][0]:
				frappe.throw(_("Rule Code <b> ' {0} '</b> And Revision : <b> {1} </b> already exist for Party : <b>{2}</b> ").format(self.rule_code,self.revision_number,self.party_name))

		from erpnext.controllers.status_updater import validate_status
		validate_status(self.status, ["Active", "Closed", "Cancelled"])

	def on_submit(self):
		self.update_prevdoc()

	def update_prevdoc(self):
		if self.amended_from:
			prev_to_date =frappe.utils.get_datetime(frappe.utils.add_days(getdate(self.from_date), -1)).strftime('%Y-%m-%d')
			frappe.db.set_value('Wage Rule', self.amended_from, 'to_date', prev_to_date)

	def validate_prevdoc_dates(self):
		if self.amended_from:
			prev_doc = frappe.get_doc("Wage Rule", self.amended_from)
			if not (getdate(self.from_date) > getdate(prev_doc.from_date)) and prev_doc.docstatus !=2:
				frappe.throw(_("From Date should be greater than '{0}'").format(getdate(prev_doc.from_date).strftime('%d-%m-%Y')))

	TOTALCOSTTOCOMPANY = TOTALALLOWANCES= TOTALMARGIN = WAGERATE = NHAMOUNT = REIMBURSEAMT = GUARDBOARDLEVY = TOTALEARN = TOTALPERCOST = TOTALDEFFREDCOST = RELIVINGCOST = RETDAYS = EARNEDBASIC = EARNEDDA = EARNEDHRA = EARNEDEA = EARNEDCA = EMONBONUS = EMONLEAVE = EARNEDSA = EARNEDWA = EARNEDPA = EXTRADUTY = EDAMOUNT = GROSS = PTAXAMT = CALCESI = CALCBASIC = BONUSAMT = LEAVEWAGE = UNIFORMCOST = TRAININGCOST = ESIEMPLOYEECONT = PFEMPLOYEECONT = PFEMPLOYERCONT = GRATUITY = PFADMIN = LWFAMT = ESIEMPLOYERCONT = FPFEMPLOYEE = FPFEMPLOYER = NHAMOUNT =0.00

	def fn_calculate_cost(self):
		print("################################ fn_calculate_cost() Calcutae Costing Started ##################################")

		FROM_DATE= getdate(self.from_date) # get date object from getdate()
		TOTAL_DAYS_IN_MONTH = calendar.monthrange(FROM_DATE.year, FROM_DATE.month)[1] # get last day day in paassed month and year
		#print("@@@@@@@@@@@ Last Day of Current Month(from_date) @@@@@@@@@@@@@@@", TOTAL_DAYS_IN_MONTH)

		if self.rate_inclusive_of_reliving_charges.upper() == "NO":
			self.WAGERATE = flt(self.rate + (self.rate / 6))
		else: self.WAGERATE = flt(self.rate)

		#print("@@@@@@@@@@self.WAGERATE @@@@@@@@@@@@@",self.WAGERATE)

		self.NHAMOUNT = flt(self.fn_nhamount(0)) # call fn_nhamount() to calculate National Holiday Amount

		############## CALDAY ###################
		if self.wage_days.upper() == "FIXED":
			self.RETDAYS = flt(self.total_wage_days)
		elif self.wage_days.upper() == "VARYING":
			self.RETDAYS = flt(TOTAL_DAYS_IN_MONTH)
		#else: self.RETDAYS = flt(self.number_of_duties) - (30 - flt(self.total_wage_days))

		self.EARNEDBASIC 	= flt(self.wage_basic) / self.RETDAYS * flt(self.number_of_duties)
		self.EARNEDDA 		= flt(self.dearness_allowance) / self.RETDAYS * flt(self.number_of_duties)
		self.EARNEDHRA 		= flt(self.hra_allowance) / self.RETDAYS * flt(self.number_of_duties)
		self.EARNEDEA 		= flt(self.educational_allowance) / self.RETDAYS * flt(self.number_of_duties)
		self.EARNEDCA 		= flt(self.conveyance_allowance) / self.RETDAYS * flt(self.number_of_duties)
		self.EMONBONUS 		= (flt(self.bonus_amount) / self.RETDAYS) * flt(self.number_of_duties)
		self.EMONLEAVE 		= (flt(self.leave_wages_amount) / self.RETDAYS) * flt(self.number_of_duties)
		self.EARNEDSA		= flt(self.special_allowance) / self.RETDAYS * flt(self.number_of_duties)
		self.EARNEDWA 		= flt(self.washing_allowance) / self.RETDAYS * flt(self.number_of_duties)
		self.EARNEDPA 		= round((flt(self.performance_allowance) / self.RETDAYS) * flt(self.number_of_duties))

		############## ED ###################
		if self.wage_hours > 0 and self.contract_hours > 0:
			self.EXTRADUTY = flt(flt(flt(flt(self.contract_hours - self.wage_hours) * self.number_of_duties) / self.wage_hours) / 2)
		else :self.EXTRADUTY = 0.0
		############## EDAMOUNT ###################
		ED_CALC_AMT= 0.00
		if self.extra_duty_applicable.upper() == "YES":
			if self.extra_duty_gross_pay_based.upper() == "YES":
				ED_CALC_AMT = self.wage_basic + self.dearness_allowance + self.conveyance_allowance + self.hra_allowance + self.special_allowance + self.washing_allowance + self.educational_allowance
			else: ED_CALC_AMT = self.wage_basic + self.dearness_allowance + self.special_allowance
		else: ED_CALC_AMT= 0.00

		self.EDAMOUNT = round(flt((self.EXTRADUTY * 2 * ED_CALC_AMT) / self.RETDAYS))

		self.GROSS = round(self.EARNEDBASIC + self.EARNEDDA + self.EARNEDHRA + self.EARNEDEA + self.EARNEDCA + self.EMONBONUS + self.EMONLEAVE + self.EARNEDSA + self.EARNEDWA)

		if self.professional_tax_applicable.upper() == "YES":
			if (self.GROSS + self.EDAMOUNT) < 2500: self.PTAXAMT= 0.0
			elif (self.GROSS + self.EDAMOUNT) < 3501: self.PTAXAMT= 60
			elif (self.GROSS + self.EDAMOUNT) < 5001: self.PTAXAMT= 120
			elif (self.GROSS + self.EDAMOUNT) < 10001: self.PTAXAMT= 175
			else: self.PTAXAMT = 200
		else: pass

		self.CALCESI	= round(self.GROSS + self.EDAMOUNT + self.NHAMOUNT + self.EARNEDPA - self.EARNEDWA)
		self.CALCBASIC	= flt(self.EARNEDBASIC + self.EARNEDDA + self.EARNEDSA)

		if self.bonus.upper() == "YES":
			self.BONUSAMT = round(self.CALCBASIC * 0.0833)
		elif self.bonus.upper() == "GUARD BOARD":
			self.BONUSAMT = round(self.CALCBASIC * 0.1)
		else: pass

		if self.leave_wages_applicable.upper() == "YES":
			self.LEAVEWAGE = round((self.CALCBASIC * 0.06))
		else: pass

		if self.uniform_charges.upper() == "STANDARD":
			self.UNIFORMCOST = round(self.CALCBASIC * 0.04)
		elif self.uniform_charges.upper() == "VARYING":
			self.UNIFORMCOST = round(float(self.uniform_charges_amount))
		else: pass

		if self.training_and_charges.upper() == "STANDARD":
			self.TRAININGCOST = round(self.CALCBASIC * 0.06)
		elif self.training_and_charges.upper() == "VARYING":
			self.TRAININGCOST = round(float(self.training_charges_amount))
		else: pass

		if self.esi_applicable.upper() == "YES":
			self.ESIEMPLOYERCONT = math.ceil(self.CALCESI * 0.0475)
		else:pass

		if self.esi_applicable.upper() == "YES":
			self.ESIEMPLOYEECONT = math.ceil(self.CALCESI * 0.0175)
		else: pass

		if self.gratuity_applicable.upper() == "YES":
			self.GRATUITY = round(flt(self.CALCBASIC * 0.04))
		else: pass

		if self.pf_applicable.upper() == "YES":
			self.PFADMIN = round(flt(self.CALCBASIC * 0.01))
		else: pass

		if self.labour_welfare_fund_applicable.upper() == "YES":
			#frmdate = datetime.strptime(str(self.from_date), '%Y-%m-%d')
			#frmdate = getdate(self.from_date)
			if FROM_DATE.month == 6 or FROM_DATE.month == 12: self.LWFAMT = 12
			else: pass
		else: pass

		################### PF EMPLOYEE CONTRIBUTION ########################
		if self.pf_applicable.upper() == "YES":
			self.PFEMPLOYEECONT = round(flt(self.CALCBASIC * 0.12))
		else:pass

		################### FPF EMPLOYEE CONTRIBUTION ########################
		if self.pf_applicable.upper() == "YES" or self.pf_applicable.upper() == "CUSTOMER":
			if flt(self.CALCBASIC) > 15000.00: self.FPFEMPLOYEE = round(15000 * 0.12)
			else:self.FPFEMPLOYEE = round(self.CALCBASIC * 0.12)
		else: pass

		################### FPF EMPLOYER CONTRIBUTION ########################
		if self.pf_applicable.upper() == "YES" or self.pf_applicable.upper() == "CUSTOMER":
			if flt(self.CALCBASIC) > 15000.00: self.FPFEMPLOYER = round(15000 * 0.0833)
			else: self.FPFEMPLOYER = round(self.CALCBASIC * 0.0833)
		else: pass

		################### PF EMPLOYER CONTRIBUTION ########################
		if self.pf_applicable.upper() == "YES":
			self.PFEMPLOYERCONT= round((flt(self.CALCBASIC) * 0.12)- self.FPFEMPLOYER)
		elif self.pf_applicable.upper() == "CUSTOMER":
			if flt(self.CALCBASIC) > 15000.00: self.PFEMPLOYERCONT = round(flt(15000.00 * 0.12))
			else:self.PFEMPLOYERCONT = round(self.CALCBASIC * 0.12)
		else: pass

		################### RELIEVING COST ########################
		if self.guard_board_levy_applicable.upper() == "YES":
			self.GUARDBOARDLEVY= round(((self.CALCBASIC * 3.0) / 100))
		else: pass
		self.TOTALEARN= self.GROSS + self.EDAMOUNT + self.NHAMOUNT + self.EARNEDPA + self.REIMBURSEAMT
		self.TOTALPERCOST= self.PFEMPLOYERCONT + self.FPFEMPLOYER + self.PFADMIN + self.ESIEMPLOYERCONT
		self.TOTALDEFFREDCOST= self.LEAVEWAGE + self.BONUSAMT + self.GRATUITY + self.GUARDBOARDLEVY
		reliving_on = 0.0
		reliving_on = self.TOTALEARN + self.TOTALPERCOST + self.TOTALDEFFREDCOST + self.UNIFORMCOST + self.TRAININGCOST
		if self.reliving_charges.upper() == "STANDARD":
			self.RELIVINGCOST = round((reliving_on * 1 / 6))
		elif self.reliving_charges.upper() == "VARYING":
			self.RELIVINGCOST = float(self.reliving_charges_amount)
		else: pass
		self.TOTALCOSTTOCOMPANY = round(
			self.EARNEDBASIC + self.EARNEDDA + self.EARNEDHRA + self.EARNEDCA + self.EARNEDEA + self.EARNEDSA +
			self.EARNEDWA + self.EARNEDPA + self.EMONBONUS + self.EMONLEAVE + self.REIMBURSEAMT + self.EDAMOUNT +
			self.NHAMOUNT + self.ESIEMPLOYERCONT + self.PFEMPLOYERCONT + self.FPFEMPLOYER + self.BONUSAMT +
			self.LEAVEWAGE + self.UNIFORMCOST + self.TRAININGCOST + self.GRATUITY + self.PFADMIN + self.RELIVINGCOST)

		self.TOTALMARGIN= round(self.WAGERATE - self.TOTALCOSTTOCOMPANY)
		self.EMPONHANDNET= round(self.TOTALEARN - self.ESIEMPLOYEECONT - self.PFEMPLOYEECONT - self.PTAXAMT - self.LWFAMT)

		self.TOTALALLOWANCES= self.EARNEDHRA + self.EARNEDCA + self.EARNEDEA + self.EARNEDSA + self.EARNEDWA + self.EARNEDPA + self.EMONBONUS + self.EMONLEAVE + self.REIMBURSEAMT + self.EDAMOUNT + self.NHAMOUNT
		print("################################ fn_calculate_cost() Calcutae Costing Complete ##################################")
		#return True

	def make_revision(source_name, target_doc=None):
		target_doc = get_mapped_doc("Wage Rule", source_name, {
			"Wage Rule": {
				"doctype": "Wage Rule",
				"validation": {
					"docstatus": ["=", 1]
				}
			}
		}, target_doc)
		return target_doc

	def fn_nhamount(self, NH):
		if self.national_holidays_applicable.upper() == "YES":
			if self.extra_duty_gross_pay_based.upper() == "YES":
				NHAMOUNT = flt((NH * self.GROSS) / self.number_of_duties)
			else: NHAMOUNT = flt((NH * self.CALCBASIC) / self.number_of_duties)
		else: pass
		return round(NHAMOUNT)
