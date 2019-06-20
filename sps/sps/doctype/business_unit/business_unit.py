# -*- coding: utf-8 -*-
# Copyright (c) 2018, TUSHAR TAJNE and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.contacts.address_and_contact import load_address_and_contact, delete_contact_and_address
from frappe import _

class BusinessUnit(Document):
	def onload(self):
		"""Load address and contacts in `__onload`"""
		load_address_and_contact(self)

	def validate(self):
		name = str(self.bu_code).upper()
		self.name = _(name)
	def on_trash(self):
		delete_contact_and_address('Buisness Unit', self.name)
		if frappe.db.exists("Customer", self.bu_name):
			frappe.delete_doc("Customer", frappe.db.exists("Customer", self.bu_name))
	def create_primary_address(self):
		if self.flags.is_new_doc and self.get('address_line1'):
			make_address(self)

	def on_update(self):
		# create customer from bu type customer
		self.create_primary_address()
		if self.bu_type == "Customer":
			exist_list=frappe.get_all('Customer', filters={'customer_code': self.bu_code}, fields=['name', 'customer_name'])
			if not exist_list:
				customer = frappe.new_doc("Customer")
				customer.customer_code = self.bu_code
				customer.customer_name = self.bu_name
				if self.status == "Active":	customer.disabled = 0
				else: customer.disabled = 1
				customer.customer_type = "Company"
				customer.customer_group = "Commercial"
				customer.territory = "All Territories"
				customer.append('links', dict(link_doctype='Business Unit', link_name=self.name,link_title=self.bu_name ))
				customer.flags.ignore_permissions = self.flags.ignore_permissions
				customer.autoname()
				if not frappe.db.exists("Customer", self.bu_name):
					customer.insert()
				else:
					doc = frappe.get_doc("Customer", self.bu_name)
					doc.customer_code = self.bu_code
					doc.customer_name = self.bu_name
					if self.status == "Active":	doc.disabled = 0
					else:doc.disabled = 1
					doc.append('links',dict(link_doctype='Business Unit', link_name=self.name, link_title=self.bu_name))
					doc.flags.ignore_permissions = self.flags.ignore_permissions
					doc.save()
				#else : frappe.throw(_("Customer : '{0}' already exist").format(self.bu_name))

@frappe.whitelist()
def get_children(doctype, parent, bu_type, is_root=False):
	#parent_fieldname = 'parent_' + doctype.lower().replace(' ', '_')
	parent_fieldname = 'business_unit'
	fields = [
		'name as value','bu_type as type',
		'is_group as expandable'
	]
	filters = [['docstatus', '<', 2]]
	if is_root:
		fields += ['bu_type'] if doctype == 'Business Unit' else []
		filters.append(['ifnull(`{0}`,"")'.format(parent_fieldname), '=', '' if is_root else parent])
		filters.append(['bu_type', '=', bu_type])
	else:
		parent_fieldname2 = 'business_unit'
		filters.append(['ifnull(`{0}`,"")'.format(parent_fieldname2), '=', '' if is_root else parent])
	acc = frappe.get_list(doctype, fields=fields, filters=filters)
	return acc

def make_address(args, is_primary_address=1):
	address = frappe.get_doc({
		'doctype': 'Address',
		'address_title': args.get('name'),
		'address_line1': args.get('address_line1'),
		'address_line2': args.get('address_line2'),
		'city': args.get('city'),
		'state': args.get('state'),
		'pincode': args.get('pincode'),
		'country': args.get('country'),
		'links': [{
			'link_doctype': args.get('doctype'),
			'link_name': args.get('name')
		}]
	}).insert()

	return address


@frappe.whitelist()
def get_youtility_data(param):
	import requests, json, datetime
	param= eval(param)
	head= {"Accept":"applicaiton/json", "Content-type": "application/json"}
	if str(param["web_service"]) == "Business Unit":
		fetch= frappe.db.sql("Select url, deviceid, loginid, password, query, last_synced, servicename, sitecode, story, tzoffset, name from `tabAPI Services` where web_service= '%s';" % (str(param["web_service"])))
		post_data= {
                        "deviceid"    : str(fetch[0][1]),
                        "loginid"     : str(fetch[0][2]),
                        "password"    : str(fetch[0][3]),
                        "query"       : str(fetch[0][4]).replace("&gt;", ">").replace("&lt;", "<").replace("\n", " ") % ('1970-01-01 00:00:00' if fetch[0][5] is None else fetch[0][5].strftime("%Y-%m-%d %H:%M:%S")),
                        "servicename" : str(fetch[0][6]),
                        "sitecode"    : str(fetch[0][7]),
                        "story"       : str(fetch[0][8]),
                        "tzoffset"    : str(fetch[0][9]),
					}
		response= requests.post( fetch[0][0], data= json.dumps(post_data))
		print response.json()	
		if response.json()["rc"] == 0:
			if response.json()["nrow"] > 0:
				coltypelist= columnlist = rowlist = None
				coltypelist= response.json()["coltype"][1:].split(response.json()["coltype"][:1])
				columnlist=  response.json()["columns"][1:].split(response.json()["columns"][:1])
				rowlist=     response.json()["row_data"][1:].split(response.json()["row_data"][:1])
				R= []
				for row in range(0, len(rowlist)):
					r= rowlist[row][1:].split(rowlist[row][:1])
					R.append(r)
				D=[]
				for i in range(0, len(R)):
					d={}
					for j in range(0, len(columnlist)):
						d[columnlist[j]]= R[i][j]
						D.append(d)
				print D
				bu_id= frappe.db.sql("select bu_id, bu_code from `tabBusiness Unit`")
				buid_list= []
				imported_row_count= 0
				updated_row_count = 0
				for r in range(0, len(bu_id)):
					buid_list.append(bu_id[r][0])
				for i in range(0, len(D)):
					if D[i]["buid"] in buid_list:
						doc_name= frappe.db.sql("select name from `tabBusiness Unit` where bu_id= '%s';" %(str(D[i]["buid"])))
						print doc_name
						frappe.db.set_value("Business Unit", doc_name[0][0], "bu_id",         D[i]["buid"])
						frappe.db.set_value("Business Unit", doc_name[0][0], "bu_code",       D[i]["bucode"])
						frappe.db.set_value("Business Unit", doc_name[0][0], "bu_name",       D[i]["buname"])
						frappe.db.set_value("Business Unit", doc_name[0][0], "bu_type",       D[i]["butype"])
						frappe.db.set_value("Business Unit", doc_name[0][0], "business_unit", D[i]["parent"])
						updated_row_count +=1
					else:
						er= frappe.new_doc("Business Unit")
						er.bu_id=         D[i]["buid"]
						er.bu_code=       D[i]["bucode"]
						er.bu_name=       D[i]["buname"]
						er.bu_type=       D[i]["butype"]
						er.businss_unit=  D[i]["parent"]			
						er.save()
						imported_row_count= imported_row_count + 1
						doc= frappe.get_doc("API Services", fetch[0][10])
						frappe.db.set_value("API Services", doc.name , "last_synced", datetime.datetime.now())
						frappe.db.commit()
						msg= "Total %d Data Updated successfully! and %d Data Imported successfully!" %(updated_row_count, imported_row_count)
			else: msg= "No Updates !! Data is Already Upto Date."
		else: msg= "Data Import failed"
		return msg
