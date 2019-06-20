frappe.listview_settings['Wage Rule'] = {
	add_fields: ["status"],
	filters: [["status","=", "Active"]],
	get_indicator: function(doc) {
		var indicator = [__(doc.status), frappe.utils.guess_colour(doc.status), "status,=," + doc.status];
		indicator[1] = {"Active": "green", "Closed": "darkgrey", "Cancelled": "red"}[doc.status];
		return indicator;
	}
};