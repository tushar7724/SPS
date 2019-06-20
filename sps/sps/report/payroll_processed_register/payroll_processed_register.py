# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt
from frappe import _

def execute(filters=None):
	if not filters: filters = {}
	################ Get filtered Payroll Processed Data #################
	payroll_processed_list = get_payroll_processed_list(filters)
	if not payroll_processed_list: return [], []

	################ Get Earning & Deduction Columns #################
	columns, earning_types, ded_types = get_columns(payroll_processed_list)

	################ Validate Component exist or not #################
	earning_comp = ['basic', 'dearness allowance', 'house rent allowance', 'conveyance allowance', 'washing allowance','special allowance', 'education allowance',
					'extra duty amount', 'national holiday amount', 'performance allowance', 'bonus amount','leave amount']
	new_list = [n for n in earning_comp if n not in earning_types]
	if new_list:
		frappe.msgprint("Earning Component %s not exist."% (', '.join(new_list).upper()))
		return [], []

	################ Get Earning & Deduction Values Map #################
	ss_earning_map = get_ss_earning_map(payroll_processed_list)
	ss_ded_map = get_ss_ded_map(payroll_processed_list)

	#print"@@@@@@@@@@@@ ss_ded_map @@@@@@@@@@@@@@@@",ss_ded_map
	data = []
	count=0
	for ss in payroll_processed_list:
		count+=1
		################ Get Linked Doc Values #################
		if ss.customer:
			customer_code = frappe.get_value("Customer", ss.customer, "customer_code")
		if ss.wage_rule_details:
			wage_info = frappe.get_doc("Wage Rule Details", ss.wage_rule_details).as_dict()
		if ss.emp_id:
			emp_info = frappe.get_doc("Employee", ss.emp_id).as_dict()

		row = [ss.name, ss.company,ss.period, ss.start_date, ss.end_date, ss.contract, ss.attendance, ss.branch, customer_code,
			   	ss.customer, ss.site, ss.site_name, ss.emp_id, ss.emp_name,ss.work_type,
		   		ss.present_duty,ss.week_off,ss.extra_duty,ss.attendance_national_holidays, ss.total_duty]

		if not ss.period == None:columns[2] = columns[2].replace('-1','50')
		#if not ss.customer  == None: columns[5] = columns[5].replace('-1','120')
		if not ss.customer  == None: columns[10] = columns[10].replace('-1','150')
		if not ss.site  == None: columns[11] = columns[11].replace('-1','80')
		if not ss.site_name  == None: columns[12] = columns[12].replace('-1','130')
		#if not ss.leave_withut_pay  == None: columns[9] = columns[9].replace('-1','130')

		################### APPEND ALL EARNINGS + GROSS COLUMNS VALUES ######################
		#for earning_comp in ss.earnings:
			#if earning_comp.basic:row.append(earning_comp.basic)
			#print"###### earning_comp ################",earning_comp


		row.append(ss_earning_map.get(ss.name, {}).get('basic'))
		row.append(ss_earning_map.get(ss.name, {}).get('dearness allowance'))
		row.append(ss_earning_map.get(ss.name, {}).get('house rent allowance'))
		row.append(ss_earning_map.get(ss.name, {}).get('conveyance allowance'))
		row.append(ss_earning_map.get(ss.name, {}).get('washing allowance'))
		row.append(ss_earning_map.get(ss.name, {}).get('special allowance'))
		row.append(ss_earning_map.get(ss.name, {}).get('education allowance'))

		row += [ss.total_pd]

		row.append(ss_earning_map.get(ss.name, {}).get('extra duty amount'))
		row.append(ss_earning_map.get(ss.name, {}).get('national holiday amount'))
		row.append(ss_earning_map.get(ss.name, {}).get('performance allowance'))
		row.append(ss_earning_map.get(ss.name, {}).get('bonus amount'))
		row.append(ss_earning_map.get(ss.name, {}).get('leave amount'))

		row += [ss.gross]

		row.append(ss_ded_map.get(ss.name, {}).get('provident fund'))
		row.append(ss_ded_map.get(ss.name, {}).get('employee state insurance'))
		row.append(ss_ded_map.get(ss.name, {}).get('labour welfare fund'))
		row.append(ss_ded_map.get(ss.name, {}).get('professional tax'))
		row.append(ss_ded_map.get(ss.name, {}).get('tax deduction'))
		row.append(ss_ded_map.get(ss.name, {}).get('total advances'))

		row += [ss.total_deduction, ss.net_pay]

		row += [emp_info.bank_ac_no,emp_info.date_of_joining,emp_info.department,emp_info.pf_number,emp_info.esi_number,emp_info.esi_zone]

		row += [ss.pay_slip_status,ss.paid_on,ss.payout_no]

		wage_rule_state = frappe.db.get_value("Salary Structure", ss.wage_rule,'state')
		row += [ss.wage_rule,wage_rule_state]
		row += [wage_info.revision, wage_info.wage_basic, wage_info.dearness_allowance, wage_info.hra_allowance, wage_info.conveyance_allowance,
				wage_info.washing_allowance, wage_info.special_allowance, wage_info.performance_allowance]

		wr_total_earnings = float(float(wage_info.wage_basic) + float(wage_info.dearness_allowance) + float(wage_info.hra_allowance)
						+ float(wage_info.conveyance_allowance) + float(wage_info.washing_allowance) + float(wage_info.special_allowance)
					  	+ float(wage_info.performance_allowance))
		row += [wr_total_earnings]
		data.append(row)
	print"###################### Payroll Processed Register Report Created : %s #####################"%count
	return columns, data

def get_columns(payroll_processed_list):
	columns = [
		_("ID") + ":Link/Processed Payroll:120", _("Company") + ":Link/Company:120",_("Pay Period") + ":Link/Payroll Period:-1",_("Start Date") + "::80", _("End Date") + "::80",
		_("Contract") + ":Link/Contract:120",_("Attendance") + ":Link/SPS Attendance:120",	_("Branch") + ":Link/Branch:120",
		_("Customer Code") + "::120",_("Customer") + ":Link/Customer:-1",_("Site Code") + ":-1", _("Site") + ":Link/Business Unit:-1",
		_("Employee Id") + ":Link/Employee:80", _("Employee Name") + "::140", _("Work Type") + ":Link/Work Type:120", _("PD") + ":Float:50",
		_("WO") + ":Float:50",_("ED") + ":Float::50",_("NH") + ":Float::50",_("Total Duty") + ":Float:80" #20 columns
	]

	################### ALL EARNINGS + GROSS COLUMNS ######################
	columns = columns + [_("Basic") + ":Float:100",_("DA") + ":Float:100",_("HRA") + ":Float:100",_("CA") + ":Float:100",_("WA") + ":Float:100",
						 _("SA") + ":Float:100",_("EA") + ":Float:100",_("PD Amount") + ":Currency:100"] # 8 columns

	columns = columns + [_("ED Amount") + ":Float:100", _("NH Amount") + ":Float:100", _("PA") + ":Float:100", _("Bonus Amount") + ":Float:100",
						 _("Leave Amount") + ":Float:100",_("Total Earning") + ":Currency:120"] #6 columns

	################### ALL Deduction + Total Ded COLUMNS ######################
	columns = columns + [_("PF") + ":Float:100", _("ESI") + ":Float:100", _("L.W.F") + ":Float:100",_("P.Tax") + ":Float:100", _("TDS") + ":Float:100",
						 _("Advances") + ":Float:100",_("Total Deduction") + ":Currency:120",_("Net Pay") + ":Currency:120"] #8 columns

	################### ALL Deduction + Total Ded COLUMNS ######################
	columns = columns + [_("A/C No") + ":Data:100",_("DOJ") + "::80",_("Department") + "::140",_("PF Number") + "::140",_("ESI Number") + "::140",_("ESI Zone") + "::100"]

	################### PAYOUT DETAILS ######################
	columns = columns + [_("Pay Status") + "::50", _("Paid On") + "::80", _("Payout No") + "::50"]

	################### Wage Rule DETAILS ######################
	columns = columns + [_("Wage Rule") + "::50", _("State") + "::80", _("Revision") + "::80", _("WR-Basic") + ":Float:100",_("WR-DA") + ":Float:100", _("WR-HRA") + ":Float:100",
						 _("WR-CA") + ":Float:100", _("WR-WA") + ":Float:100", _("WR-SA") + ":Float:100", _("WR-PA") + ":Float:100", _("WR-Total Earnings") + ":Currency:100"]

	salary_components = {_("Earning"): [], _("Deduction"): []}

	for component in frappe.db.sql("""select distinct sd.salary_component, sc.type
		from `tabSalary Detail` sd, `tabSalary Component` sc
		where sc.name=sd.salary_component and sd.parent in (%s)""" %
		(', '.join(['%s']*len(payroll_processed_list))), tuple([d.name for d in payroll_processed_list]), as_dict=1):
		salary_components[_(component.type)].append(str(component.salary_component).lower())

	return columns, salary_components[_("Earning")], salary_components[_("Deduction")]

def get_payroll_processed_list(filters):
	#filters.update({"start_date": filters.get("start_date"), "end_date":filters.get("end_date")})
	filters.update({"period": filters.get("period")})
	conditions, filters = get_conditions(filters)
	payroll_processed_list = frappe.db.sql("""select * from `tabProcessed Payroll` where %s """ % conditions, filters, as_dict=1)

	"""if payroll_processed_list:
		for pp in payroll_processed_list:
			pp_doc = frappe.get_doc('Processed Payroll', pp.name)
			for pp_row in pp_doc.get('earnings'):
				print"###### kk ################", pp_row.salary_component
	"""
	return payroll_processed_list or []
def get_salary_structure(pp):
	salary_structure = frappe.db.sql("""select * from `tabSalary Structure` ss, `tabWage Rule Details` wrd where wrd.parent = %s""" % pp, as_dict=1)
	return salary_structure or []

def get_conditions(filters):
	conditions = ""
	doc_status = {"Draft": 0, "Submitted": 1, "Cancelled": 2}

	if filters.get("docstatus"):
		conditions += "docstatus = {0}".format(doc_status[filters.get("docstatus")])

	if filters.get("company"): conditions += " and company = %(company)s"
	if filters.get("period"): conditions += " and period = %(period)s"
	if filters.get("employee"): conditions += " and emp_id = %(employee)s"

	return conditions, filters

def get_ss_earning_map(payroll_processed_list):
	ss_earnings = frappe.db.sql("""select parent, salary_component, amount
		from `tabSalary Detail` where parent in (%s)""" %
		(', '.join(['%s']*len(payroll_processed_list))), tuple([d.name for d in payroll_processed_list]), as_dict=1)

	ss_earning_map = {}
	for d in ss_earnings:
		ss_earning_map.setdefault(d.parent, frappe._dict()).setdefault(d.salary_component, [])
		ss_earning_map[d.parent][str(d.salary_component).lower()] = flt(d.amount)

	return ss_earning_map

def get_ss_ded_map(payroll_processed_list):
	ss_deductions = frappe.db.sql("""select parent, salary_component, amount
		from `tabSalary Detail` where parent in (%s)""" %
		(', '.join(['%s']*len(payroll_processed_list))), tuple([d.name for d in payroll_processed_list]), as_dict=1)

	ss_ded_map = {}
	for d in ss_deductions:
		ss_ded_map.setdefault(d.parent, frappe._dict()).setdefault(d.salary_component, [])
		ss_ded_map[d.parent][str(d.salary_component).lower()] = flt(d.amount)

	return ss_ded_map