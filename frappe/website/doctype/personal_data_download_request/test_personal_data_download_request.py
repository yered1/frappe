# -*- coding: utf-8 -*-
# Copyright (c) 2019, Frappe Technologies and Contributors
# See license.txt
from __future__ import unicode_literals

import frappe
import unittest
import json
from frappe.website.doctype.personal_data_download_request.personal_data_download_request import get_user_data


class TestRequestPersonalData(unittest.TestCase):
	def setUp(self):
		create_user_if_not_exists(email='test_privacy@example.com')

	def test_user_data_creation(self):
		user_data = json.loads(get_user_data('test_privacy@example.com'))
		expected_data = {'Contact': frappe.get_all('Contact', {'email_id':'test_privacy@example.com'}, ["*"])}
		expected_data = json.loads(json.dumps(expected_data, default=str))
		self.assertEqual({'Contact': user_data['Contact']}, expected_data)

	def test_file_and_email_creation(self):
		frappe.set_user('test_privacy@example.com')
		download_request = frappe.get_doc({"doctype": 'Personal Data Download Request', 'user': 'test_privacy@example.com'})
		download_request.save(ignore_permissions=True)
		frappe.set_user('Administrator')

		f = frappe.get_all('File',
			{'attached_to_doctype':'Personal Data Download Request', 'attached_to_name': download_request.name},
			['*'])
		self.assertEqual(len(f), 1)

		email_queue = frappe.db.sql("""SELECT *
			FROM `tabEmail Queue`
			ORDER BY `creation` DESC""", as_dict=True)
		self.assertTrue("Subject: Download Your Data" in email_queue[0].message)

		frappe.db.sql("delete from `tabEmail Queue`")

def create_user_if_not_exists(email, first_name = None):
	if frappe.db.exists("User", email):
		return

	frappe.get_doc({
		"doctype": "User",
		"user_type": "Website User",
		"email": email,
		"send_welcome_email": 0,
		"first_name": first_name or email.split("@")[0],
		"birth_date": frappe.utils.now_datetime()
	}).insert(ignore_permissions=True)
