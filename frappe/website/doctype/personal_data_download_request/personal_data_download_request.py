# -*- coding: utf-8 -*-
# Copyright (c) 2019, Frappe Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import json
from frappe import _
from frappe.model.document import Document
from frappe.utils.verified_command import get_signed_params

class PersonalDataDownloadRequest(Document):
	def after_insert(self):
		if frappe.session.user in ['Administrator', 'Guest']:
			frappe.throw(_("This user cannot request to download data"))
		else:
			personal_data = get_user_data(frappe.session.user)
			self.generate_file_and_send_mail(personal_data)

	def generate_file_and_send_mail(self, personal_data):
		"""generate the file link for download"""
		user_name = self.user_name.replace(' ','-')
		f = frappe.get_doc({
			'doctype': 'File',
			'file_name': 'Personal-Data-'+user_name+'-'+self.name+'.json',
			"attached_to_doctype": 'Personal Data Download Request',
			"attached_to_name": self.name,
			'content': str(personal_data),
			'is_private': 1
		})
		f.save(ignore_permissions=True)

		file_link = frappe.utils.get_url("/api/method/frappe.core.doctype.file.file.download_file") +\
			"?" + get_signed_params({"file_url": f.file_url})
		host_name = frappe.local.site
		frappe.sendmail(
			recipients=frappe.session.user,
			subject=_("Download Your Data"),
			template="download_data",
			args={
				'user':frappe.session.user,
				'user_name':self.user_name,
				'link':file_link,
				'host_name':host_name
			},
			header=[_("Download Your Data"), "green"]
		)

def get_user_data(user):
	""" returns user data not linked to User doctype """
	hooks = frappe.get_hooks("user_privacy_documents")
	data = {}
	for hook in hooks:
		d = data.get(hook.get('doctype'),[])
		d += frappe.get_all(hook.get('doctype'), {hook.get('match_field'): user}, ["*"])
		if d:
			data.update({ hook.get('doctype'):d })
	return json.dumps(data, indent=2, default=str)