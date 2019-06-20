# -*- coding: utf-8 -*-
# Copyright (c) 2018, TUSHAR TAJNE and contributors
# For license information, please see license.txt


from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import getdate
from frappe import _
from calendar import month_abbr
class PeriodMaster(Document):
	def validate(self):
		if self.from_date == self.to_date:
			frappe.throw(_("From-Date And To-Date can Not be same"))
		else: pass
		sqlres = frappe.db.sql("""select name from `tabPeriod Master` where from_date = '%s' and to_date= '%s' """ % (self.from_date, self.to_date))
		if sqlres != ():
			if sqlres[0][0] != self.name:
				frappe.throw(_("Period Already Exist. <b> From ' {0} to {1}'</b>").format(self.from_date,self.to_date))
			else:
				return True
		else: return True
	pass
