# Copyright (c) 2013, TUSHAR TAJNE and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt, cint
from frappe import _
from frappe.utils import date_diff
from erpnext import get_company_currency, get_default_company

def execute(filters=None):
	if not filters:
		return [], []

	if filters.get("period"):
		period = frappe.get_doc("Payroll Period", filters.get("period")).as_dict()
	data = columns = []
	if filters.get("period") and period :
		if filters.get("company"):
			currency = get_company_currency(filters["company"])
		else:
			company = get_default_company()
			currency = get_company_currency(company)

		columns = columns + [
			_("Customer") + ":Link/Customer:220",
			_("Site Code") + ":Link/Business Unit:100",
			_("Site Name") + "::220",
			_("Contract") + ":Link/Contract:180",
			_("Work Type") + "::150",
			_("Qty") + ":Float:30",
			_("Att.Days") + ":Float:40",
			_("Contract Duty") + ":Float:40",
			_("Att.Duty") + ":Float:40",
			_("Inv Duty") + ":Float:40",
			_("Payable Duty") + ":Float:60",
			_("Payroll Duty") + ":Float:60"
		]

		filters.update({"start_date": period.start_date,"end_date": period.end_date})
		contract_list = get_all_active_contracts(filters) or []
		if contract_list:
			all_tree = {}
			for contract in contract_list:

				############## Get attendance details work type wise ############
				attendance_wt = get_attendance_wt_duties(filters, contract.name)
				#print ":::::::::::::::: Contract : '%s' :::::::: \n WT Total Attendance duties : '%s' ::::::::::::"% (contract.name,attendance_wt)
				wt_attendance_duties = 0

				si_wt = get_bill_wt_duties(filters, contract.party_name, contract.name)
				#print ":::::::::::::::: Contract : '%s' :::::::: \n WT Total SI duties : '%s' :::::" % (contract.name, si_wt)
				wt_si_duties = 0.00

				payroll_wt = get_payroll_wt_duties(filters, contract.name)
				wt_payroll_duties = 0.00

				if contract.start_date > period.start_date:	frmdt = contract.start_date
				else : frmdt = period.start_date

				if contract.end_date < period.end_date: todt = contract.end_date
				else : todt = period.end_date

				############# Attendance Days calculation ################
				period_days = date_diff(todt, frmdt) + 1

				"""if contract.party_name not in all_tree.keys():
					all_tree[contract.party_name] = {contract.bu_site: {contract.name: []}}
				else:
					print"############## all_tree ########", all_tree
					if contract.bu_site not in all_tree[contract.party_name].keys():
						all_tree[contract.party_name][contract.bu_site]= {contract.name: []}
						if contract.name not in all_tree[contract.party_name][contract.bu_site].keys():
							all_tree[contract.party_name][contract.bu_site][contract.bu_site] = []
					else: all_tree[contract.party_name][contract.bu_site][contract.name] += []

				#print"############## all_tree ########", all_tree
				"""
				contract_details = frappe.db.sql("""select * from `tabContract Details` where parent ='%s' """ % (contract.name), as_dict=1)
				if contract_details:

					for cd in contract_details:

						if cd.work_type in attendance_wt.keys():
							wt_attendance_duties = attendance_wt[cd.work_type]["wt_attendance_duties"]

						if cd.work_type in si_wt.keys():
							wt_si_duties = si_wt[cd.work_type]["wt_si_duties"]

						if cd.work_type in payroll_wt.keys():
							wt_payroll_duties = payroll_wt[cd.work_type]["wt_payroll_duties"]

						if filters.get("type") == "Attendance Zero":
							if wt_attendance_duties < 1:
								row = [
									contract.party_name, contract.bu_site, contract.bu_site_name, contract.name, cd.work_type, cd.quantity, period_days,
									(cd.quantity * period_days), wt_attendance_duties, wt_si_duties,"" or 0.00, wt_payroll_duties
								]
								data.append(row)
						elif filters.get("type") == "To Bill":
							if wt_si_duties < 1:
								row = [
									contract.party_name, contract.bu_site, contract.bu_site_name, contract.name, cd.work_type, cd.quantity, period_days,
									(cd.quantity * period_days), wt_attendance_duties, wt_si_duties, ""or 0.00, wt_payroll_duties
								]
								data.append(row)
						else :
							row = [
								contract.party_name, contract.bu_site, contract.bu_site_name, contract.name,
								cd.work_type, cd.quantity, period_days,
								(cd.quantity * period_days), wt_attendance_duties, wt_si_duties, 0.00, wt_payroll_duties
							]
							data.append(row)

	return columns, data

def get_all_active_contracts(filters):
	conditions = ""
	if filters.get("customer"):
		conditions += "and party_name = '{0}'".format(filters.get("customer"))
	if filters.get("site"):
		conditions += "and  bu_site = '{0}'".format(filters.get("site"))

	if filters.get("contract"):
		conditions += "and  name = '{0}'".format(filters.get("contract"))

	#print"########## conditions ########",conditions
	contract_list = frappe.db.sql("""select * from `tabContract` where start_date <= '%s' and end_date >= '%s' and docstatus=1 and status='Active' %s """ % (filters.end_date, filters.start_date, conditions), as_dict=1)
	return contract_list

def get_attendance_wt_duties(filters, contract):
	wt_ad_details = {}
	att_name=None
	att_wo_included=None
	for d in frappe.db.sql("""select name,weekly_off_included from `tabSPS Attendance` where attendance_period = '%s' and contract ='%s' and docstatus=1 LIMIT 1""" % (filters.get("period"), contract),as_dict=1):
		att_name= d.name
		att_wo_included= d.weekly_off_included

	#print"################# Attendance : '%s' :::::::::: W/Off : '%s'#################"%(att_name,att_wo_included)
	if att_name:
		for ad in frappe.db.sql("""select * from `tabAttendance Details` where parent = '%s' """ % att_name,as_dict=1):
			wt_attendance_duties=0.00
			if att_wo_included == 1: wt_attendance_duties = flt(ad.present_duty + ad.week_off + ad.extra_duty)
			else: wt_attendance_duties = flt(ad.present_duty + ad.extra_duty)

			if ad.work_type not in wt_ad_details.keys():
				wt_ad_details[ad.work_type] = {'wt_attendance_duties': wt_attendance_duties}
			else: wt_ad_details[ad.work_type]["wt_attendance_duties"] += wt_attendance_duties
	return wt_ad_details or {}

def get_bill_wt_duties(filters, customer, contract):
	wt_si_details = {}
	si_filters = [['docstatus', '=', 1], ['is_return', '=', 0],
				  ['billing_type', 'in', ['Standard', 'Attendance', 'Supplementary']], ['customer', '=', customer],
				  ['billing_period', '=', filters.get("period")]]

	si_list = frappe.get_list("Sales Invoice", fields=['name'], filters=si_filters)
	for si in si_list:
		for si_item in frappe.db.sql("""select item_code,qty from `tabSales Invoice Item` where parent = '%s' and contract = '%s' """ % (si.name,contract),as_dict=1):
			if si_item.item_code not in wt_si_details.keys():
				wt_si_details[si_item.item_code] = {'wt_si_duties': si_item.qty or 0}
			else: wt_si_details[si_item.item_code]["wt_si_duties"] += si_item.qty or 0
	return wt_si_details or {}

def get_payroll_wt_duties(filters, contract):
	wt_payroll_details = {}
	for pd in frappe.db.sql(
					"""select work_type,staff_worked_days from `tabProcessed Payroll`
					where period = '%s' and contract ='%s' and docstatus=1 LIMIT 1""" % (
					filters.get("period"), contract), as_dict=1):
		if pd.work_type not in wt_payroll_details.keys():
			wt_payroll_details[pd.work_type] = {'wt_payroll_duties': pd.staff_worked_days}
		else:
			wt_payroll_details[pd.work_type]["wt_payroll_duties"] += pd.staff_worked_days
	return wt_payroll_details or {}