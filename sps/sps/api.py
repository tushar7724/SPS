from __future__ import unicode_literals
import frappe 

@frappe.whitelist(allow_guest=True)
def sps_erpnext_rest_api(filters = None):
	return_output= ""
	print " @@@@@@@ filter @@@@@@@@@ ", filters 
	if filters and filters != None:
		filters= eval(filters)
		print"@@@@@@@@@@ REST Called @@@@@@@@@@@@@@@@"
		return_output=  "Attendance data sent successfuly !!"
	else: return_output= "Data is not valid !!"
	return {"message": return_output}
