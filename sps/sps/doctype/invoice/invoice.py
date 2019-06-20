# -*- coding: utf-8 -*-
# Copyright (c) 2018, TUSHAR TAJNE and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.desk import tags
from frappe import _

class Invoice(Document):
	def autoname(self):
		name = str(self.party) +"/"+ str(self.month) + "-" + str(self.year)
		self.name = _(name)
	pass

	def validate(self):
		print"@@@@@@@@ Tag @@@@@@",tags
	pass
