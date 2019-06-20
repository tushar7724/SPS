# -*- coding: utf-8 -*-
# Copyright (c) 2018, TUSHAR TAJNE and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class WorkType(Document):
	def on_update(self):
		if self.name:
			item = frappe.new_doc("Item")
			item.update({
				"name": self.name,
				"item_code": self.name,
				"item_name": self.name,
				"item_group": "Services",
				"stock_uom": "Nos",
				"is_stock_item": 0,
				"allow_transfer_for_manufacture": 0,
				"is_purchase_item": 0
			})
			item.insert()
