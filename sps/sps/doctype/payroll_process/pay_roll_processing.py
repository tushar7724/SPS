# -*- coding: utf-8 -*-
# Copyright (c) 2019, TUSHAR TAJNE and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import date_diff, getdate

class PayRollProcessing(Document):
	def calculate_payment(self):
		data= frappe.get_list('SPS Attendance', filters={'docstatus': 1, 'attendance_period': self.period}, fields= ['name'])
		pay_details= []
		for at in range(0,len(data)):
			attendance_doc= frappe.get_doc('SPS Attendance', data[at].name).as_dict()
			for attd in range(0, len(attendance_doc.attendance_details)):
				emp_att_details= attendance_doc.attendance_details[attd]	
				wage_rule= self.get_wage_rule(emp_att_details)
				emp_payment_details= self.calculate_emp_payment(emp_att_details, wage_rule)
				emp_payment_details["emp_name"]= emp_att_details.employee_name
				emp_payment_details["emp_id"]= emp_att_details.employee
				emp_payment_details["emp_work_type"]= emp_att_details.work_type
				emp_payment_details["emp_PD"]= emp_att_details.present_duty
				emp_payment_details["emp_ED"]= emp_att_details.extra_duty
				emp_payment_details["emp_WO"]= emp_att_details.weak_off
				emp_payment_details["emp_NH"]= emp_att_details.national_holidays
				emp_payment_details["emp_bill_duty"]= emp_att_details.bill_duty
				emp_payment_details["emp_payroll_duty"]= emp_att_details.payroll_duty
				emp_payment_details["emp_wage_rule"]= emp_att_details.wage_rule
				emp_payment_details["emp_wage_rule_revision"]= wage_rule.revision
				emp_payment_details["emp_customer"]= attendance_doc.customer 
				emp_payment_details["emp_contract"]= attendance_doc.contract
				pay_details.append(emp_payment_details)
		print pay_details
		return "bohot hard bohot hard"
		
	def get_wage_rule(self, attendance):
		employee_wage_rule= frappe.get_doc('Salary Structure', attendance.wage_rule).as_dict()
		if len(employee_wage_rule.wage_rule_details) > 0:
			wage_rule= None
			for wgr in range(0, len(employee_wage_rule.wage_rule_details)):
				if len(employee_wage_rule.wage_rule_details) > 1:
					wage_rule_fdt= getdate(employee_wage_rule.wage_rule_details[wgr].from_date)
					wage_rule_tdt= getdate(employee_wage_rule.wage_rule_details[wgr].to_date)
					if wage_rule_fdt <= getdate(self.start_date) and wage_rule_tdt <= getdate(self.end_date): 
						wage_rule= employee_wage_rule.wage_rule_details[wgr]
						break
				else:   
					wage_rule= employee_wage_rule.wage_rule_details[0]                      
		return wage_rule

	def calculate_emp_payment(self, emp_details, wage_rule):
		import calendar, math
		from erpnext.hr.doctype.salary_structure.salary_structure import fn_ptax_state_wise, fn_lwf_state_wise
		emp_payment_details= {}
		RETDAYS= NHAMOUNT= PFADMIN= PFEMPLOYEECONT= FPFEMPLOYEE= FPFEMPLOYER= PFEMPLOYERCONT= GUARDBOARDLEVY= 0.00
		EARNEDBASIC = EARNEDDA = EARNEDHRA = EARNEDEA = EARNEDCA = EMONBONUS = EMONLEAVE = EARNEDSA = 0.00
	        EARNEDWA = EARNEDPA = EXTRADUTY = EDAMOUNT = GROSS = PTAXAMT = CALCESI = CALCBASIC = BONUSAMT = 0.00
		LEAVEWAGE= ESIEMPLOYERCONT= TOTALEARN= REIMBURSEAMT= PTAXAMT= LWFAMT= ESIEMPLOYEECONT= GRATUITY= 0.00
		UNIFORMCOST = TRAININGCOST = RATE= 0.00
		total_duties= emp_details.present_duty + emp_details.week_off
		emp_payment_details["total_duties"]= total_duties
		if wage_rule.wage_days.upper() == "FIXED":
			RETDAYS = float(wage_rule.total_wage_days)
			if wage_rule.rate_per == "Duty":
				RATE= round(float(wage_rule.total_wage_days) * (wage_rule.rate/ float(wage_rule.number_of_duties)), 2)
			elif wage_rule.rate_per == "Month":
				RATE= round((wage_rule.rate/ float(wage_rule.number_of_duties)) * wage_rule.total_wage_days, 2)
			else: pass
		elif wage_rule.wage_days.upper() == "VARYING":
			RETDAYS = float(TOTAL_DAYS_IN_MONTH)
			if wage_rule.rate_per == "Duty":
				RATE= round(float(RETDAYS) * (wage_rule.rate/ float(wage_rule.number_of_duties)), 2)
			elif wage_rule.rate_per == "Month":
				RATE= round((wage_rule.rate/ float(wage_rule.number_of_duties)) * float(RETDAYS), 2)
			else: pass
		else: pass
		emp_payment_details["RATE"]= RATE 
		emp_payment_details["RETDAYS"]= RETDAYS 
		EARNEDBASIC = round(float(wage_rule.wage_basic)             / RETDAYS * float(total_duties), 2)
		EARNEDDA    = round(float(wage_rule.dearness_allowance)     / RETDAYS * float(total_duties), 2)
		EARNEDHRA   = round(float(wage_rule.hra_allowance)          / RETDAYS * float(total_duties), 2)
		EARNEDEA    = round(float(wage_rule.educational_allowance)  / RETDAYS * float(total_duties), 2)
		EARNEDCA    = round(float(wage_rule.conveyance_allowance)   / RETDAYS * float(total_duties), 2)
		EMONBONUS   = round(float(wage_rule.bonus_amount)           / RETDAYS * float(total_duties), 2)
		EMONLEAVE   = round(float(wage_rule.leave_wages_amount)     / RETDAYS * float(total_duties), 2)
		EARNEDSA    = round(float(wage_rule.special_allowance)      / RETDAYS * float(total_duties), 2)
		EARNEDWA    = round(float(wage_rule.washing_allowance)      / RETDAYS * float(total_duties), 2)
		EARNEDPA    = round(float(wage_rule.performance_allowance)  / RETDAYS * float(total_duties), 2)
		emp_payment_details["EARNEDBASIC"]= EARNEDBASIC
		emp_payment_details["EARNEDDA"]   = EARNEDDA
		emp_payment_details["EARNEDHRA"]  = EARNEDHRA
		emp_payment_details["EARNEDEA"]   = EARNEDEA
		emp_payment_details["EARNEDCA"]   = EARNEDCA
		emp_payment_details["EMONBONUS"]  = EMONBONUS
		emp_payment_details["EMONLEAVE"]  = EMONLEAVE
		emp_payment_details["EARNEDSA"]   = EARNEDSA
		emp_payment_details["EARNEDWA"]   = EARNEDWA
		emp_payment_details["EARNEDPA"]   = EARNEDPA
		### Calculating extra duty ######
		ED_CALC_AMT= 0.00
                if wage_rule.extra_duty_applicable.upper() == "YES":
                	if wage_rule.extra_duty_gross_pay_based.upper() == "YES":
                        	ED_CALC_AMT = wage_rule.wage_basic + wage_rule.dearness_allowance + wage_rule.conveyance_allowance + wage_rule.hra_allowance + wage_rule.special_allowance + wage_rule.washing_allowance + wage_rule.educational_allowance
                        else: ED_CALC_AMT = wage_rule.wage_basic + wage_rule.dearness_allowance + wage_rule.special_allowance
                else: ED_CALC_AMT= 0.00
		EDAMOUNT= round(float((emp_details.extra_duty * 2 * ED_CALC_AMT) / RETDAYS), 2)
		emp_payment_details["EDAMOUNT"]= EDAMOUNT
		GROSS= round(EARNEDBASIC + EARNEDDA + EARNEDHRA + EARNEDEA + EARNEDCA + EMONBONUS + EMONLEAVE + EARNEDSA + EARNEDWA, 2)
		emp_payment_details["GROSS"]= GROSS
		################### BASE FOR CAL OTHER DEDUCTION##########
		CALCBASIC= float(EARNEDBASIC + EARNEDDA + EARNEDSA)
		emp_payment_details["CALCBASIC"]= CALCBASIC
		################### UNIFORM CHARGES ######################
		if wage_rule.uniform_charges.upper() == "STANDARD":
                                UNIFORMCOST = round(CALCBASIC * 0.04)
                elif wage_rule.uniform_charges.upper() == "VARYING":
                                UNIFORMCOST = round(float(wage_rule.uniform_charges_amount))
                else: pass
		emp_payment_details["UNIFORMCOST"]= UNIFORMCOST
		################### TRAINING CHARGES #####################
                if wage_rule.training_and_charges.upper() == "STANDARD":
                                TRAININGCOST = round(CALCBASIC * 0.06)
                elif wage_rule.training_and_charges.upper() == "VARYING":
                                TRAININGCOST = round(float(wage_rule.training_charges_amount))
                else: pass
		emp_payment_details["TRAININGCOST"]= TRAININGCOST
		################### NATIONAL HOLIDAY AMOUNT###############
		NHAMOUNT= self.fn_nhamount(wage_rule.national_holidays_applicable, wage_rule.extra_duty_gross_pay_based, GROSS, CALCBASIC, RETDAYS, emp_details.national_holidays)
		emp_payment_details["NHAMOUNT"]= NHAMOUNT
		################### BASE FOR CAL ESI #####################
                CALCESI= round(GROSS + EDAMOUNT + NHAMOUNT + EARNEDPA - EARNEDWA, 2)
		emp_payment_details["CALCESI"]= CALCESI
		################### BONUS AMOUNT #########################
		BONUSAMT= self.fn_bonus_amount(wage_rule.bonus, CALCBASIC)
		emp_payment_details["BONUSAMT"]= BONUSAMT
		################### LEAV EWAGE  ##########################
		if wage_rule.leave_wages_applicable.upper() == "YES":
                	LEAVEWAGE= round((CALCBASIC * 0.06), 2)
                else: pass
		emp_payment_details["LEAVEWAGE"]= LEAVEWAGE
		################### ESI EMPLOYER CONT  ###################
		if wage_rule.esi_applicable.upper() == "YES":
			ESIEMPLOYERCONT = math.ceil(CALCESI * 0.0475)
		else:pass
		emp_payment_details["ESIEMPLOYERCONT"]= ESIEMPLOYERCONT
		################### TOTAL EARNING  #######################
 		TOTALEARN= GROSS + EDAMOUNT + NHAMOUNT + EARNEDPA + REIMBURSEAMT		
		emp_payment_details["TOTALEARN"]= TOTALEARN
		################### PROFESSIONAL TAX  ####################
		state= frappe.db.get_value("Salary Structure", wage_rule.parent, "state")
		PTAXAMT= fn_ptax_state_wise(wage_rule.professional_tax_applicable, TOTALEARN, state)
		emp_payment_details["PTAXAMT"]= PTAXAMT
		from_date= getdate(self.start_date)
		################### LABOUR WALFARE FUND  #################
		LWFAMT=  fn_lwf_state_wise(wage_rule.labour_welfare_fund_applicable, from_date, state)
		emp_payment_details["LWFAMT"]= LWFAMT	
		################### ESI EMPLOYEE CONT   ##################
		if wage_rule.esi_applicable.upper() == "YES":
			ESIEMPLOYEECONT = math.ceil(CALCESI * 0.0175)
		else: pass
		emp_payment_details["ESIEMPLOYEECONT"]= ESIEMPLOYEECONT
		################### GRATUITY  ############################
		if wage_rule.gratuity_applicable.upper() == "YES":
			GRATUITY = round(float(CALCBASIC * 0.04), 2)
		else: pass
		emp_payment_details["GRATUITY"]= GRATUITY
		################### PF ADMIN CHARGES #####################
		if wage_rule.pf_applicable.upper() == "YES":
			PFADMIN = round(float(CALCBASIC * 0.01), 2)
		else: pass
		emp_payment_details["PFADMIN"]= PFADMIN
		################### PF EMPLOYEE CONT #####################
		if wage_rule.pf_applicable.upper() == "YES":
			PFEMPLOYEECONT = round(float(CALCBASIC * 0.12), 2)
		else:pass
		emp_payment_details["PFEMPLOYEECONT"]= PFEMPLOYEECONT
		################### FPF EMPLOYEE CONTRIBUTION ############
		if wage_rule.pf_applicable.upper() == "YES" or wage_rule.pf_applicable.upper() == "CUSTOMER":
			if float(CALCBASIC) > 15000.00: FPFEMPLOYEE = round(15000 * 0.12, 2)
			else:FPFEMPLOYEE = round(CALCBASIC * 0.12, 2)
		else: pass
		emp_payment_details["FPFEMPLOYEE"]= FPFEMPLOYEE
		################### FPF EMPLOYER CONTRIBUTION #############
		if wage_rule.pf_applicable.upper() == "YES" or wage_rule.pf_applicable.upper() == "CUSTOMER":
			if float(CALCBASIC) > 15000.00: FPFEMPLOYER = round(15000 * 0.0833, 2)
			else: FPFEMPLOYER = round(CALCBASIC * 0.0833, 2)
		else: pass
		emp_payment_details["FPFEMPLOYER"]= FPFEMPLOYER
		################### PF EMPLOYER CONTRIBUTION ##############
		if wage_rule.pf_applicable.upper() == "YES":
			PFEMPLOYERCONT= round((float(CALCBASIC) * 0.12)- FPFEMPLOYER, 2)
		elif wage_rule.pf_applicable.upper() == "CUSTOMER":
			if float(CALCBASIC) > 15000.00: PFEMPLOYERCONT = round(float(15000.00 * 0.12), 2)
			else:PFEMPLOYERCONT = round(CALCBASIC * 0.12, 2)
		else: pass
		emp_payment_details["PFEMPLOYERCONT"]= PFEMPLOYERCONT
		################### GUARDBOARD LEVY #######################
		if wage_rule.guard_board_levy_applicable.upper() == "YES":
			GUARDBOARDLEVY= round((CALCBASIC * 3.0) / 100, 2)
		else: pass
		emp_payment_details["GUARDBOARDLEVY"]= GUARDBOARDLEVY
		extra_deduction= self.calculate_extra_deduction(emp_details.employee)
		emp_payment_details["extra_deduction"]= extra_deduction
		TOTALPERCOST= PFEMPLOYERCONT + FPFEMPLOYER + PFADMIN + ESIEMPLOYERCONT
		emp_payment_details["TOTALPERCOST"]= TOTALPERCOST
		TOTALDEFFREDCOST= LEAVEWAGE + BONUSAMT + GRATUITY + GUARDBOARDLEVY
		emp_payment_details["TOTALDEFFREDCOST"]= TOTALDEFFREDCOST
		TOTALCOSTTOCOMPANY = round(
					EARNEDBASIC + EARNEDDA        + EARNEDHRA      + EARNEDCA    + EARNEDEA     + EARNEDSA  +
					EARNEDWA    + EARNEDPA        + EMONBONUS      + EMONLEAVE   + REIMBURSEAMT + EDAMOUNT  +
					NHAMOUNT    + ESIEMPLOYERCONT + PFEMPLOYERCONT + FPFEMPLOYER + BONUSAMT     + LEAVEWAGE + 
					UNIFORMCOST + TRAININGCOST    + GRATUITY       + PFADMIN
					)
		emp_payment_details["TOTALCOSTTOCOMPANY"]= TOTALCOSTTOCOMPANY
		TOTALMARGIN= round(RATE - TOTALCOSTTOCOMPANY)
		emp_payment_details["TOTALMARGIN"]= TOTALMARGIN
		EMPINHANDNET= round(TOTALEARN - ESIEMPLOYEECONT - PFEMPLOYEECONT - PTAXAMT - LWFAMT)
		emp_payment_details["EMPINHANDNET"]= EMPINHANDNET
		return emp_payment_details

	def fn_nhamount(self, national_holidays_applicable, extra_duty_gross_pay_based, GROSS, CALCBASIC, RETDAYS, NH):
		NHAMOUNT= 0.00
		if national_holidays_applicable.upper() == "YES":
			if extra_duty_gross_pay_based.upper() == "YES":
				NHAMOUNT = float((NH * GROSS)          / RETDAYS)
			else: NHAMOUNT   = float((NH * CALCGROSSBASIC) / RETDAYS)
		else: pass
		return round(NHAMOUNT)

	def fn_bonus_amount(self, bonus, CALCBASIC):
		BONUSAMT= 0.00
		if bonus.upper() == "YES":
			BONUSAMT = round(CALCBASIC * 0.0833, 2)
		elif bonus.upper() == "GUARD BOARD":
			BONUSAMT = round(CALCBASIC * 0.1, 2)
		elif bonus.upper() == "CUSTOMER SPECIFIC":
			if CALCBASIC < 7000:BONUSAMT = round(CALCBASIC * 0.0833, 2)
			else: round(7000 * 0.0833, 2) 
		else: pass
		return BONUSAMT

	def calculate_extra_deduction(self, emp_id):
		deduction= frappe.db.sql("""SELECT ln.loan_type, rs.total_payment, rs.name, rs.parent
					    FROM `tabRepayment Schedule` rs
					    INNER JOIN tabLoan ln ON rs.parent= ln.name WHERE ln.applicant = '%s'
					    AND rs.paid= 0 AND rs.payment_date BETWEEN '%s' AND '%s';""" %(emp_id, self.start_date, self.end_date), as_dict= True)
		emp_fcl= {}
		if len(deduction) > 0:
			for chrg in range(0, len(deduction)):
				emp_fcl[str(deduction[chrg]["loan_type"])]= deduction[chrg]["total_payment"]
				loan= frappe.get_doc("Loan", deduction[chrg]["parent"])
				frappe.db.set_value("Repayment Schedule", deduction[chrg]["name"], "paid", 1, update_modified=True)
				
		return emp_fcl
