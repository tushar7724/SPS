# -*- coding: utf-8 -*-
# Copyright (c) 2019, TUSHAR TAJNE and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt, cint
from frappe.model.document import Document
from frappe.utils import date_diff, getdate

class PayrollProcess(Document):
	def delete_processed_entry(self):
		msg= ""
		temp= frappe.get_list('Processed Payroll', filters={'payroll_process': self.name}, fields= ['name'])
		if len(temp) > 0:
			data= frappe.get_list('Processed Payroll', filters={'pay_slip_status': 'Paid', 'payroll_process': self.name}, fields= ['name'])
			if len(data) > 0:
				msg= "Can not delete record salary slip genereted" 
			else:
				data= frappe.get_list('Processed Payroll', filters={'pay_slip_status': 'Prepared', 'payroll_process': self.name}, fields= ['name'])
				for i in range(0, len(data)):
					processed_payroll= frappe.get_doc('Processed Payroll', data[i]["name"])
					self.calculate_extra_deduction(processed_payroll.emp_id, 1)
					processed_payroll.cancel()
					processed_payroll.delete()
				msg=  "Records deleted Successfully"
		else : msg=  "No record found for deletion"
		return msg
	
	def validate(self):
		self.check_payroll_entry()
		self.attendance_to_be_processed()

	def check_payroll_entry(self):
		temp= None
		if self.additional_filter == "Attendance":
			temp= frappe.db.sql("""select name from `tabProcessed Payroll` where attendance= '%s' and period= '%s';""" %(self.attendance, self.period))
			if len(temp) > 1:
				frappe.throw("Payroll Process Already Done For Given Criteria")
			else: pass
		else: pass

	def check_invocing(self, attendance):		
		pass
	def processed_attendance(self):
		attendances= ()
		processed_attendance= []
		if self.additional_filter == "Customer":
			if self.site == None or self.site == "":
				attendances= frappe.db.sql("""select distinct attendance from `tabProcessed Payroll` where period= '%s' and  customer = '%s'""" %(self.period, self.customer))
			else:
				attendances= frappe.db.sql("""select distinct attendance from `tabProcessed Payroll` where period= '%s' and  customer = '%s' and site = '%s'""" %(self.period, self.customer, self.site))
		elif self.additional_filter == "" or self.additional_filter == None:
			attendances= frappe.db.sql("""select distinct attendance from `tabProcessed Payroll` where period= '%s'""" %(self.period))
		else: pass
		for i in range(0, len(attendances)):
			processed_attendance.append(str(attendances[i][0]))
		return processed_attendance

	def attendance_to_be_processed(self):
		processed_attendance= self.processed_attendance()
		data=[]
		if self.additional_filter == "Customer":
			if self.site == None or self.site == "":
				data= frappe.get_list('SPS Attendance', filters={'docstatus': 1, 'attendance_period': self.period, 'customer': self.customer, 'name' : ("not in",processed_attendance )}, fields= ['name'])
			else:
				data= frappe.get_list('SPS Attendance', filters={'docstatus': 1, 'attendance_period': self.period, 'customer': self.customer, 'site': self.site, 'name' : ("not in",processed_attendance )}, fields= ['name'])
		elif self.additional_filter == "Attendance":
			data= frappe.get_list('SPS Attendance', filters={'docstatus': 1, 'attendance_period': self.period, 'name': self.attendance}, fields= ['name'])
		else:
			data= frappe.get_list('SPS Attendance', filters={'docstatus': 1, 'attendance_period': self.period, 'name' : ("not in",processed_attendance )}, fields= ['name'])
		if len(data) < 1:
			frappe.throw("Attedance not found for given criteria Or All Attendance Already Processed")
		else:pass
		return  data

	def calculate_payment(self):
		data= self.attendance_to_be_processed()
		pay_details= []
		for at in range(0,len(data)):
			attendance_doc= frappe.get_doc('SPS Attendance', data[at].name).as_dict()
			for attd in range(0, len(attendance_doc.attendance_details)):
				emp_att_details= attendance_doc.attendance_details[attd]
				#wage_rule= frappe.get_doc("Wage Rule Details", emp_att_details.wage_rule_details).as_dict()
				wage_rule= self.get_wage_rule(attendance_doc.attendance_details[attd])
				emp_payment_details= self.calculate_emp_payment(emp_att_details, wage_rule, attendance_doc)
				pay_details.append(emp_payment_details)
		return pay_details

	def get_wage_rule(self, attendance):
		employee_wage_rule= frappe.get_doc('Salary Structure', attendance.wage_rule).as_dict()
		wage_rule= None
		if len(employee_wage_rule.wage_rule_details) > 0:
			for wgr in range(0, len(employee_wage_rule.wage_rule_details)):
				if len(employee_wage_rule.wage_rule_details) > 1:
					wage_rule_fdt= getdate(employee_wage_rule.wage_rule_details[wgr].from_date)
					wage_rule_tdt= getdate(employee_wage_rule.wage_rule_details[wgr].to_date)
					if wage_rule_fdt <= getdate(self.start_date) and wage_rule_tdt >= getdate(self.end_date):
						wage_rule= employee_wage_rule.wage_rule_details[wgr] if employee_wage_rule.wage_rule_details[wgr] else frappe.throw("Wage Rule not found for employee %s in attendance %s" %(attendance.employee, attendance.parent))
						break
				else:
					wage_rule= employee_wage_rule.wage_rule_details[0]
		else:
			frappe.throw("Wage Rule not found for employee %s in attendance %s" %(attendance.employee, attendance.parent))
		return wage_rule

	def create_payout(self,employee=None, wage_rule=None):
		filters = [['docstatus', '=', 1], ['period', '=', self.period], ['pay_slip_status', '=', 'Prepared'],['company', '=', self.company]]
		if employee:
			filters.append(['emp_id', '=', employee])
		if wage_rule:
			filters.append(['wage_rule', '=', wage_rule])
		pp_list = frappe.get_list('Processed Payroll', fields=['*'], filters=filters)
		if pp_list:
			args = frappe._dict({
				#"salary_slip_based_on_timesheet": self.salary_slip_based_on_timesheet,
				"payroll_frequency": self.payroll_frequency,
				"start_date": self.start_date,
				"end_date": self.end_date,
				"company": self.company,
				"posting_date": self.posting_date,
				#"deduct_tax_for_unclaimed_employee_benefits": self.deduct_tax_for_unclaimed_employee_benefits,
				#"deduct_tax_for_unsubmitted_tax_exemption_proof": self.deduct_tax_for_unsubmitted_tax_exemption_proof,
				"payroll_process": self.name
			})
			frappe.enqueue(create_salary_slips_and_payout, timeout=4000, pp_list=pp_list, args=args)
			self.reload()
		else: frappe.throw(_("No Data Found For Payroll Process"))
		return 'queued'

	def calculate_emp_payment(self, emp_details, wage_rule, attendance_doc):
		import calendar, math
		from erpnext.hr.doctype.salary_structure.salary_structure import fn_ptax_state_wise, fn_lwf_state_wise
		emp_payment_details= {}
		RETDAYS= NHAMOUNT= PFADMIN= PFEMPLOYEECONT= FPFEMPLOYEE= FPFEMPLOYER= PFEMPLOYERCONT= GUARDBOARDLEVY= 0.00
		EARNEDBASIC = EARNEDDA = EARNEDHRA = EARNEDEA = EARNEDCA = EMONBONUS = EMONLEAVE = EARNEDSA = 0.00
		EARNEDWA = EARNEDPA = EXTRADUTY = EDAMOUNT = GROSS = PTAXAMT = CALCESI = CALCBASIC = BONUSAMT = 0.00
		LEAVEWAGE= ESIEMPLOYERCONT= TOTALEARN= REIMBURSEAMT= PTAXAMT= LWFAMT= ESIEMPLOYEECONT= GRATUITY= 0.00
		UNIFORMCOST = TRAININGCOST = RATE= FULLBASIC= 0.00
		total_duties= emp_details.present_duty + emp_details.week_off
		FULLBASIC= float(wage_rule.wage_basic +
						 wage_rule.dearness_allowance +
						 wage_rule.educational_allowance +
						 wage_rule.conveyance_allowance +
						 wage_rule.bonus_amount +
						 wage_rule.leave_wages_amount +
						 wage_rule.special_allowance +
						 wage_rule.performance_allowance) #same as calc basic but actual comp value will
		emp_payment_details["emp_id"]= emp_details.employee
		emp_payment_details["emp_work_type"]= emp_details.work_type
		emp_payment_details["emp_PD"]= emp_details.present_duty
		emp_payment_details["emp_ED"]= emp_details.extra_duty + self.extra_duty(wage_rule.contract_hours, wage_rule.wage_hours, emp_details.present_duty + (emp_details.extra_duty * 2))
		emp_payment_details["emp_WO"]= emp_details.week_off
		emp_payment_details["emp_NH"]= emp_details.national_holidays
		emp_payment_details["emp_bill_duty"]= emp_details.bill_duty
		emp_payment_details["emp_payroll_duty"]= emp_details.payroll_duty
		emp_payment_details["emp_wage_rule"]= emp_details.wage_rule
		emp_payment_details["emp_customer"]= attendance_doc.customer
		emp_payment_details["emp_contract"]= attendance_doc.contract
		emp_payment_details["emp_attendance_code"]= attendance_doc.name
		emp_payment_details["emp_attendance_name"]= attendance_doc.attendance_name
		emp_payment_details["company"]= attendance_doc.company
		emp_payment_details["wage_rule_details"]= wage_rule
		emp_payment_details["branch"] = attendance_doc.branch
		emp_payment_details["emp_total_duties"]= total_duties
		TOTAL_DAYS_IN_MONTH = calendar.monthrange(getdate(self.start_date).year, getdate(self.start_date).month)[1]
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
		EARNEDBASIC = round(float(wage_rule.wage_basic)             / RETDAYS * float(total_duties), 2) if total_duties > 0  else 0.0 
		EARNEDDA    = round(float(wage_rule.dearness_allowance)     / RETDAYS * float(total_duties), 2) if total_duties > 0  else 0.0
		EARNEDHRA   = round(float(wage_rule.hra_allowance)          / RETDAYS * float(total_duties), 2) if total_duties > 0  else 0.0
		EARNEDEA    = round(float(wage_rule.educational_allowance)  / RETDAYS * float(total_duties), 2) if total_duties > 0  else 0.0
		EARNEDCA    = round(float(wage_rule.conveyance_allowance)   / RETDAYS * float(total_duties), 2) if total_duties > 0  else 0.0
		EMONBONUS   = round(float(wage_rule.bonus_amount)           / RETDAYS * float(total_duties), 2) if total_duties > 0  else 0.0
		EMONLEAVE   = round(float(wage_rule.leave_wages_amount)     / RETDAYS * float(total_duties), 2) if total_duties > 0  else 0.0
		EARNEDSA    = round(float(wage_rule.special_allowance)      / RETDAYS * float(total_duties), 2) if total_duties > 0  else 0.0
		EARNEDWA    = round(float(wage_rule.washing_allowance)      / RETDAYS * float(total_duties), 2) if total_duties > 0  else 0.0
		EARNEDPA    = round(float(wage_rule.performance_allowance)  / RETDAYS * float(total_duties), 2) if total_duties > 0  else 0.0
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
		EDAMOUNT= round(float(((emp_details.extra_duty + self.extra_duty(wage_rule.contract_hours, wage_rule.wage_hours, emp_details.present_duty + (emp_details.extra_duty * 2))) * 2 * ED_CALC_AMT) / RETDAYS), 2)
		emp_payment_details["EDAMOUNT"]= EDAMOUNT
		GROSS= round(EARNEDBASIC + EARNEDDA + EARNEDHRA + EARNEDEA + EARNEDCA + EMONBONUS + EMONLEAVE + EARNEDSA + EARNEDWA, 2)
		emp_payment_details["GROSS"]= GROSS
		################### BASE FOR CAL OTHER DEDUCTION##########
		CALCBASIC= float(EARNEDBASIC + EARNEDDA + EARNEDEA + EARNEDCA + EMONBONUS + EMONLEAVE + EARNEDSA + EARNEDPA) #8 comp except WA & HRA
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

		################### PF EMPLOYEE CONT #####################
		if wage_rule.pf_applicable.upper() == "YES":
			PFEMPLOYEECONT = round(float(CALCBASIC * 0.12), 2)
		elif wage_rule.pf_applicable.upper() == "CUSTOMER SPECIFIC":
			#if flt(CALCBASIC) > 15000.00:PFEMPLOYEECONT = round(flt(15000.00 * 0.12))
			#else: PFEMPLOYEECONT = round(float(CALCBASIC * 0.12), 2)
			#full_basic= round(EARNEDBASIC + EARNEDDA +  EARNEDEA + EARNEDCA + EMONBONUS + EMONLEAVE + EARNEDSA + EARNEDPA, 2)
			if float(FULLBASIC) > 15000:
				PFEMPLOYEECONT= round(((15000/float(FULLBASIC)) * CALCBASIC) * 0.12, 2)
			else: PFEMPLOYEECONT= round(float(CALCBASIC * 0.12), 2)			
		else:pass
		emp_payment_details["PFEMPLOYEECONT"]= PFEMPLOYEECONT
		################### PF ADMIN CHARGES #####################
		if wage_rule.pf_applicable.upper() == "YES" or wage_rule.pf_applicable.upper() == "CUSTOMER SPECIFIC":
			PFADMIN = round(float(PFEMPLOYEECONT / 12), 2)
		else:
			pass
		emp_payment_details["PFADMIN"] = PFADMIN

		################### FPF EMPLOYEE CONTRIBUTION ############
		if wage_rule.pf_applicable.upper() == "YES" or wage_rule.pf_applicable.upper() == "CUSTOMER SPECIFIC":
			if float(CALCBASIC) > 15000.00: FPFEMPLOYEE = round(15000 * 0.12, 2)
			else:FPFEMPLOYEE = round(CALCBASIC * 0.12, 2)
		else: pass
		emp_payment_details["FPFEMPLOYEE"]= FPFEMPLOYEE
		################### FPF EMPLOYER CONTRIBUTION #############
		if wage_rule.pf_applicable.upper() == "YES" or wage_rule.pf_applicable.upper() == "CUSTOMER SPECIFIC":
			if float(CALCBASIC) > 15000.00: FPFEMPLOYER = round(15000 * 0.0833, 2)
			else: FPFEMPLOYER = round(CALCBASIC * 0.0833, 2)
		else: pass
		emp_payment_details["FPFEMPLOYER"]= FPFEMPLOYER
		################### PF EMPLOYER CONTRIBUTION ##############
		if wage_rule.pf_applicable.upper() == "YES":
			PFEMPLOYERCONT= round((float(CALCBASIC) * 0.12)- FPFEMPLOYER, 2)
		elif wage_rule.pf_applicable.upper() == "CUSTOMER SPECIFIC":
			if float(CALCBASIC) > 15000.00: PFEMPLOYERCONT = round(float(15000.00 * 0.12) - FPFEMPLOYER, 2)
			else:PFEMPLOYERCONT = round(float(CALCBASIC * 0.12) - FPFEMPLOYER, 2)
		else: pass
		emp_payment_details["PFEMPLOYERCONT"]= PFEMPLOYERCONT
		################### GUARDBOARD LEVY #######################
		if wage_rule.guard_board_levy_applicable.upper() == "YES":
			GUARDBOARDLEVY= round((CALCBASIC * 3.0) / 100, 2)
		else: pass
		emp_payment_details["GUARDBOARDLEVY"]= GUARDBOARDLEVY
		extra_deduction= self.calculate_extra_deduction(emp_details.employee, 0)
		##################### EXTRA DEDUCTIONS ###################
		FINE = TC = VC = BC = CANTEEN = SALADVANCE = LOAN = TDS = 0.00
		if bool(extra_deduction):
			for k,v in extra_deduction.items():
				if k.upper() == "FINE":
					FINE = v
				if k.upper() == "TRAINING CHARGES":
					TC = v
				if k.upper() == "POLICE VERIFICATION CHARGES":
                                        VC = v
				if k.upper() == "BANK CHARGES":
                                        BC = v
				if k.upper() == "CANTEEN CHARGES":
                                        CANTEEN= v
				if k.upper() == "SALARY ADVANCE":
                                        SALADVANCE = v
				if k.upper() == "LOAN":
                                        LOAN = v
				if k.upper() == "TAX DEDUCTION":
                                        TDS = v
				pass		
		else: pass
		emp_payment_details["fine"]= FINE
		emp_payment_details["verification_charges"]= VC
		emp_payment_details["bank_charges"]= BC
		emp_payment_details["training_charges"]= TC
		emp_payment_details["canteen_charges"]= CANTEEN
		emp_payment_details["salary_advance"]= SALADVANCE
		emp_payment_details["loan"]= LOAN
		emp_payment_details["tax_deduction"]= TDS
		TOTALADVANCE= FINE + VC + BC + TC + CANTEEN + SALADVANCE + LOAN + TDS
		TOTALADV= FINE + VC + BC + TC + CANTEEN + SALADVANCE + LOAN
		emp_payment_details["TOTALADV"]= TOTALADV 
		emp_payment_details["TOTALADVANCE"]= TOTALADVANCE  	
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
		TOTALDEDUCTION = TOTALADVANCE + LWFAMT + PTAXAMT + ESIEMPLOYEECONT + PFEMPLOYEECONT
		emp_payment_details["TOTALDEDUCTION"] = TOTALDEDUCTION
		EMPINHANDNET= round(TOTALEARN - ESIEMPLOYEECONT - PFEMPLOYEECONT - PTAXAMT - LWFAMT - TOTALADVANCE)
		emp_payment_details["EMPINHANDNET"]= EMPINHANDNET
		TOTALSALCOST= TOTALEARN + PFEMPLOYERCONT + FPFEMPLOYER + PFADMIN + ESIEMPLOYERCONT
		emp_payment_details["TOTALSALCOST"] = TOTALSALCOST
		TOTAL_PD= float(EARNEDBASIC + EARNEDDA + EARNEDHRA +EARNEDCA + EARNEDEA + EARNEDSA + EARNEDWA)
		emp_payment_details["TOTAL_PD"]= TOTAL_PD
		return emp_payment_details

	def fn_nhamount(self, national_holidays_applicable, extra_duty_gross_pay_based, GROSS, CALCBASIC, RETDAYS, NH):
		NHAMOUNT= 0.00
		if national_holidays_applicable.upper() == "YES":
			if extra_duty_gross_pay_based.upper() == "YES":
				NHAMOUNT = float((NH * GROSS)          / RETDAYS)
			else: NHAMOUNT   = float((NH * CALCBASIC) / RETDAYS)
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
	def extra_duty(self, contract_hours, wage_hours, pd):
		extra_duty= 0.0
		if contract_hours > 0 and wage_hours > 0:
			if contract_hours > wage_hours:
				extra_duty= ((pd * contract_hours / wage_hours) -pd) / 2
		return extra_duty

	def calculate_extra_deduction(self, emp_id, rs):
		deduction= frappe.db.sql("""SELECT ln.loan_type, rs.total_payment, rs.name, rs.parent
					    FROM `tabRepayment Schedule` rs
					    INNER JOIN tabLoan ln ON rs.parent= ln.name WHERE ln.applicant = '%s'
					    AND rs.paid= %s AND rs.payment_date BETWEEN '%s' AND '%s';""" %(emp_id, rs, self.start_date, self.end_date), as_dict= True)
		emp_fcl= {}
		if len(deduction) > 0:
			for idx, d in enumerate(deduction):
    				if "loan_type" in d and d["loan_type"] not in emp_fcl: emp_fcl[d["loan_type"]]= 0.0
    				emp_fcl[d["loan_type"]]= emp_fcl[d["loan_type"]] + d["total_payment"]
				loan= frappe.get_doc("Loan", deduction[idx]["parent"])
				frappe.db.set_value("Repayment Schedule", deduction[idx]["name"], "paid", 1 if rs == 0 else 0, update_modified=True)
		return emp_fcl

	def create_processed_payroll_entry(self):
		self.validate()
		self.check_component_exist()
		payroll_details = self.calculate_payment()
		args = frappe._dict({
			"period": self.period,
			"name": self.name,
			"remark": self.remark
		})
		frappe.enqueue(start_processed_payroll_entry, timeout=4000, payroll_details=payroll_details,args=args)
		self.reload()
		return 'queued'

	def check_component_exist(self):
		Earning=["Basic", "Dearness Allowance", "House Rent Allowance", "Conveyance Allowance",
				"Washing Allowance", "Special Allowance", "Performance Allowance", "Education Allowance",
				"Extra Duty Amount", "National Holiday Amount", "Bonus Amount", "Leave Amount"
				]
		Deduction= ["Provident Fund",	"Employee State Insurance",	"Labour Welfare Fund",
					"Professional Tax", "Tax Deduction", "Advances", "Loan", "Canteen Charges",
					"Training Charges", "Bank Charges", "Verification Charges", "Fine", 'Total Advances'
					]
		temp= []
		sal_component= frappe.get_list("Salary Component", filters={'docstatus': 0}, fields= ['name'])
		for i in range(0, len(sal_component)):
			temp.append(str(sal_component[i]["name"]).upper())
		for i in range(0, len(Earning)):
			if Earning[i].upper() not in temp:
				sal_comp= frappe.new_doc('Salary Component')
				sal_comp.salary_component= Earning[i].capitalize()
				sal_comp.salary_component_abbr= Earning[i].capitalize()
				sal_comp.type= "Earning"
				sal_comp.save()
		for i in range(0, len(Deduction)):
			if Deduction[i].upper() not in temp:
				sal_comp= frappe.new_doc('Salary Component')
				sal_comp.salary_component= Deduction[i].capitalize()
				sal_comp.salary_component_abbr= Deduction[i].capitalize()
				sal_comp.type= "Deduction"
				sal_comp.save()

@frappe.whitelist()
def create_salary_slips_and_payout(pp_list, args, publish_progress=True):
	#salary_slips_exists_for = get_existing_salary_slips(employees, args)
	count=0
	for pp_row in pp_list:
		#if emp not in salary_slips_exists_for:
		args.update({
			"doctype": "Salary Slip",
			"processed_payroll": pp_row["name"],
			"employee": pp_row["emp_id"]

		})
		ss = frappe.get_doc(args)
		ss.insert()
		ss.submit()
		count+=1
		processed_payroll = frappe.get_doc("Processed Payroll", pp_row["name"])
		processed_payroll.db_set("pay_slip_status", 'Paid')
		processed_payroll.notify_update()

		if publish_progress:
			frappe.publish_progress(count * 100 / len(pp_list),title=_("Creating Salary Slips. It may take few minutes."))
@frappe.whitelist()
def get_employees_list(attendance):
	emp_list= []
	emp= frappe.db.sql("""select employee from `tabAttendance Details` where parent= '%s'""" %(attendance))
	if len(emp) > 0:
		for i in range(0, len(emp)):
			emp_list.append(emp[i][0])
	emp_str=  ",".join(emp_list)		
	return emp_str

@frappe.whitelist()
def start_processed_payroll_entry(payroll_details, args, publish_progress=True):
	count = 0
	for i in range(0, len(payroll_details)):
		processed_payroll = frappe.new_doc("Processed Payroll")
		processed_payroll.company = payroll_details[i]["company"]
		processed_payroll.branch = payroll_details[i]["branch"]
		processed_payroll.created_by = ""
		processed_payroll.period = args.period
		processed_payroll.payroll_process = args.name
		processed_payroll.emp_id = payroll_details[i]["emp_id"]
		processed_payroll.staff_worked_days = payroll_details[i]["emp_total_duties"]
		processed_payroll.pay_slip_status = "Prepared"
		processed_payroll.remark = args.remark
		processed_payroll.wage_rule = payroll_details[i]["emp_wage_rule"]
		processed_payroll.wage_rule_details = payroll_details[i]["wage_rule_details"].name
		processed_payroll.contract= payroll_details[i]["emp_contract"]
		######################## wage rule info to processed payroll######################################
		processed_payroll.revision = payroll_details[i]["wage_rule_details"].revision
		processed_payroll.config_code = payroll_details[i]["wage_rule_details"].config_code
		processed_payroll.type = payroll_details[i]["wage_rule_details"].type
		processed_payroll.number_of_duties = payroll_details[i]["wage_rule_details"].number_of_duties
		processed_payroll.rate_inclusive_of_reliving_charges = payroll_details[i]["wage_rule_details"].rate_inclusive_of_reliving_charges
		processed_payroll.extra_duty_double = payroll_details[i]["wage_rule_details"].extra_duty_double
		processed_payroll.over_time = payroll_details[i]["wage_rule_details"].over_time
		processed_payroll.wage_hours = payroll_details[i]["wage_rule_details"].wage_hours
		processed_payroll.contract_hours = payroll_details[i]["wage_rule_details"].contract_hours
		processed_payroll.rate_per = payroll_details[i]["wage_rule_details"].rate_per
		processed_payroll.rate = payroll_details[i]["wage_rule_details"].rate
		processed_payroll.wage_basic = payroll_details[i]["wage_rule_details"].wage_basic
		processed_payroll.dearness_allowance = payroll_details[i]["wage_rule_details"].dearness_allowance
		processed_payroll.house_rent_allowance = payroll_details[i]["wage_rule_details"].hra_allowance
		processed_payroll.conveyance_allowance = payroll_details[i]["wage_rule_details"].conveyance_allowance
		processed_payroll.washing_allowance = payroll_details[i]["wage_rule_details"].washing_allowance
		processed_payroll.special_allowance = payroll_details[i]["wage_rule_details"].special_allowance
		processed_payroll.education_allowance = payroll_details[i]["wage_rule_details"].educational_allowance
		processed_payroll.performance_allowance = payroll_details[i]["wage_rule_details"].performance_allowance
		processed_payroll.bonus_amount = payroll_details[i]["wage_rule_details"].bonus_amount
		processed_payroll.leave_amount = payroll_details[i]["wage_rule_details"].leave_wages_amount
		processed_payroll.wage_days = payroll_details[i]["wage_rule_details"].wage_days
		processed_payroll.total_wage_days = payroll_details[i]["wage_rule_details"].total_wage_days
		processed_payroll.pf_applicable = payroll_details[i]["wage_rule_details"].pf_applicable
		processed_payroll.esi_applicable = payroll_details[i]["wage_rule_details"].esi_applicable
		processed_payroll.reliving_charges = payroll_details[i]["wage_rule_details"].reliving_charges
		processed_payroll.reliving_charges_amount = payroll_details[i]["wage_rule_details"].reliving_charges_amount
		processed_payroll.bonus = payroll_details[i]["wage_rule_details"].bonus
		processed_payroll.reimbursement_applicable = payroll_details[i]["wage_rule_details"].reimbursement_applicable
		processed_payroll.extra_duty_applicable = payroll_details[i]["wage_rule_details"].extra_duty_applicable
		processed_payroll.extra_duty_gross_pay_based = payroll_details[i]["wage_rule_details"].extra_duty_gross_pay_based
		processed_payroll.professional_tax_applicable = payroll_details[i]["wage_rule_details"].professional_tax_applicable
		processed_payroll.leave_wages_applicable = payroll_details[i]["wage_rule_details"].leave_wages_applicable
		processed_payroll.guard_board_levy_applicable = payroll_details[i]["wage_rule_details"].guard_board_levy_applicable
		processed_payroll.gratuity_applicable = payroll_details[i]["wage_rule_details"].gratuity_applicable
		processed_payroll.labour_welfare_fund_applicable = payroll_details[i]["wage_rule_details"].labour_welfare_fund_applicable
		processed_payroll.wage_rule_nh = payroll_details[i]["wage_rule_details"].nh
		# processed_payroll.wage_rule_nh                   			= payroll_details[i]["wage_rule_details"].wage_rule_nh
		processed_payroll.training_and_charges = payroll_details[i]["wage_rule_details"].training_and_charges
		processed_payroll.training_charges_amount = payroll_details[i]["wage_rule_details"].training_charges_amount
		processed_payroll.uniform_charges = payroll_details[i]["wage_rule_details"].uniform_charges
		processed_payroll.uniform_charges_amount = payroll_details[i]["wage_rule_details"].uniform_charges_amount
		######################## attendance info to processed payroll######################################
		processed_payroll.attendance = payroll_details[i]["emp_attendance_code"]
		processed_payroll.work_type = payroll_details[i]["emp_work_type"]
		processed_payroll.present_duty = payroll_details[i]["emp_PD"]
		processed_payroll.week_off = payroll_details[i]["emp_WO"]
		processed_payroll.extra_duty = payroll_details[i]["emp_ED"]
		processed_payroll.attendance_national_holidays = payroll_details[i]["emp_NH"]
		processed_payroll.total_duty = payroll_details[i]["emp_total_duties"]
		processed_payroll.bill_duty = payroll_details[i]["emp_bill_duty"]
		processed_payroll.payroll_duty = payroll_details[i]["emp_payroll_duty"]
		######################## calculated deduction to processed payroll#################################
		processed_payroll.pf_employer_amount = payroll_details[i]["PFEMPLOYERCONT"]
		processed_payroll.fpf_employer_amount = payroll_details[i]["FPFEMPLOYER"]
		processed_payroll.pf_employee_amount = payroll_details[i]["PFEMPLOYEECONT"]
		processed_payroll.fpf_employee_amount = payroll_details[i]["FPFEMPLOYEE"]
		processed_payroll.pf_admin_amount = payroll_details[i]["PFADMIN"]
		processed_payroll.calcesi = payroll_details[i]["CALCESI"]
		processed_payroll.esi_employee = payroll_details[i]["ESIEMPLOYEECONT"]
		processed_payroll.esi_employer = payroll_details[i]["ESIEMPLOYERCONT"]
		processed_payroll.cal_reimbursement_amount = 0.00
		processed_payroll.professional_tax = payroll_details[i]["PTAXAMT"]
		processed_payroll.labour_welfare_fund_amount = payroll_details[i]["LWFAMT"]
		processed_payroll.gratuity_amount = payroll_details[i]["GRATUITY"]
		processed_payroll.guard_board_levy_amount = payroll_details[i]["GUARDBOARDLEVY"]
		processed_payroll.cal_uniform_amount = payroll_details[i]["UNIFORMCOST"]
		processed_payroll.cal_training_amount = payroll_details[i]["TRAININGCOST"]
		######################## calculated earning to processed payroll#############################
		processed_payroll.earned_basic = payroll_details[i]["EARNEDBASIC"]
		processed_payroll.earned_da = payroll_details[i]["EARNEDDA"]
		processed_payroll.earned_hra = payroll_details[i]["EARNEDHRA"]
		processed_payroll.earned_ca = payroll_details[i]["EARNEDCA"]
		processed_payroll.earned_wa = payroll_details[i]["EARNEDWA"]
		processed_payroll.earned_sa = payroll_details[i]["EARNEDSA"]
		processed_payroll.earned_pa = payroll_details[i]["EARNEDPA"]
		processed_payroll.earned_ea = payroll_details[i]["EARNEDEA"]
		processed_payroll.national_holiday_amount = payroll_details[i]["NHAMOUNT"]
		processed_payroll.extra_duty_amount = payroll_details[i]["EDAMOUNT"]
		processed_payroll.earned_monbonus = payroll_details[i]["EMONBONUS"]
		processed_payroll.earned_monleave = payroll_details[i]["EMONLEAVE"]
		processed_payroll.month_bonus = payroll_details[i]["BONUSAMT"]
		processed_payroll.month_leave = payroll_details[i]["LEAVEWAGE"]
		############################ Extra deductions to processed payroll #########################
		processed_payroll.fine = payroll_details[i]["fine"]
		processed_payroll.verification_charges = payroll_details[i]["verification_charges"]
		processed_payroll.bank_charges = payroll_details[i]["bank_charges"]
		processed_payroll.training_charges = payroll_details[i]["training_charges"]
		processed_payroll.canteen_charges = payroll_details[i]["canteen_charges"]
		processed_payroll.salary_advance = payroll_details[i]["salary_advance"]
		processed_payroll.loan = payroll_details[i]["loan"]
		#processed_payroll.tax_deduction = payroll_details[i]["tax_deduction"]
		############################### Other Component to processed payroll #######################
		processed_payroll.total_advances = payroll_details[i]["TOTALADVANCE"]
		processed_payroll.gross = payroll_details[i]["GROSS"]
		processed_payroll.cal_basic = payroll_details[i]["CALCESI"]
		processed_payroll.net_pay = payroll_details[i]["EMPINHANDNET"]
		processed_payroll.total_earn = payroll_details[i]["TOTALEARN"]
		processed_payroll.total_per_cost = payroll_details[i]["TOTALPERCOST"]
		processed_payroll.total_diff_cost = payroll_details[i]["TOTALDEFFREDCOST"]
		processed_payroll.total_deduction = payroll_details[i]["TOTALDEDUCTION"]
		processed_payroll.total_margin = payroll_details[i]["TOTALMARGIN"]
		processed_payroll.total_salary = payroll_details[i]["TOTALSALCOST"]
		processed_payroll.total_pd= payroll_details[i]["TOTAL_PD"]
		############################## calculated earning component to child table earnings in processed payroll##########################
		processed_payroll.append('earnings', {"salary_component": "Basic", "amount": payroll_details[i]["EARNEDBASIC"]})
		processed_payroll.append('earnings', {"salary_component": "Dearness Allowance", "amount": payroll_details[i]["EARNEDDA"]})
		processed_payroll.append('earnings', {"salary_component": "House Rent Allowance", "amount": payroll_details[i]["EARNEDHRA"]})
		processed_payroll.append('earnings', {"salary_component": "Conveyance Allowance", "amount": payroll_details[i]["EARNEDCA"]})
		processed_payroll.append('earnings', {"salary_component": "Washing Allowance", "amount": payroll_details[i]["EARNEDWA"]})
		processed_payroll.append('earnings', {"salary_component": "Special Allowance", "amount": payroll_details[i]["EARNEDSA"]})
		processed_payroll.append('earnings', {"salary_component": "Performance Allowance", "amount": payroll_details[i]["EARNEDPA"]})
		processed_payroll.append('earnings', {"salary_component": "Education Allowance", "amount": payroll_details[i]["EARNEDEA"]})
		processed_payroll.append('earnings', {"salary_component": "Extra Duty Amount", "amount": payroll_details[i]["EDAMOUNT"]})
		processed_payroll.append('earnings', {"salary_component": "National Holiday Amount", "amount": payroll_details[i]["NHAMOUNT"]})
		processed_payroll.append('earnings', {"salary_component": "Bonus Amount", "amount": payroll_details[i]["EMONBONUS"]})
		processed_payroll.append('earnings', {"salary_component": "Leave Amount", "amount": payroll_details[i]["EMONLEAVE"]})
		############################## calculated deduction component to child table deductions in processed payroll#######################
		processed_payroll.append('deductions', {"salary_component": "Provident Fund", "amount": payroll_details[i]["PFEMPLOYEECONT"]})
		processed_payroll.append('deductions', {"salary_component": "Employee State Insurance",	"amount": payroll_details[i]["ESIEMPLOYEECONT"]})
		processed_payroll.append('deductions', {"salary_component": "Labour Welfare Fund", "amount": payroll_details[i]["LWFAMT"]})
		processed_payroll.append('deductions', {"salary_component": "Professional Tax", "amount": payroll_details[i]["PTAXAMT"]})
		processed_payroll.append('deductions', {"salary_component": "Total Advances", "amount": payroll_details[i]["TOTALADV"]})
		processed_payroll.append('deductions', {"salary_component": "Tax Deduction", "amount": payroll_details[i]["tax_deduction"]})
		processed_payroll.save()
		processed_payroll.submit()
		count += 1
		if publish_progress:
			frappe.publish_progress(count * 100 / len(payroll_details),
									title=_("Creating Payroll. It may take few minutes."))
	return count
