# -*- coding: utf-8 -*-
# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# See license.txt
from __future__ import unicode_literals

import frappe
import unittest
from frappe.core.doctype.doctype.doctype import UniqueFieldnameError, IllegalMandatoryError, DoctypeLinkError, WrongOptionsDoctypeLinkError,\
 HiddenAndMandatoryWithoutDefaultError, CannotIndexedError, CannotCreateStandardDoctypeError

# test_records = frappe.get_test_records('DocType')


class TestDocType(unittest.TestCase):
	def new_doctype(self, name, unique=0, depends_on=''):
		return frappe.get_doc({
			"doctype": "DocType",
			"module": "Core",
			"custom": 1,
			"fields": [{
				"label": "Some Field",
				"fieldname": "some_fieldname",
				"fieldtype": "Data",
				"unique": unique,
				"depends_on": depends_on,
			}],
			"permissions": [{
				"role": "System Manager",
				"read": 1
			}],
			"name": name
		})

	def test_validate_name(self):
		self.assertRaises(frappe.NameError, self.new_doctype("_Some DocType").insert)
		self.assertRaises(frappe.NameError, self.new_doctype("8Some DocType").insert)
		self.assertRaises(frappe.NameError, self.new_doctype("Some (DocType)").insert)
		for name in ("Some DocType", "Some_DocType"):
			if frappe.db.exists("DocType", name):
				frappe.delete_doc("DocType", name)

			doc = self.new_doctype(name).insert()
			doc.delete()

	def test_doctype_unique_constraint_dropped(self):
		if frappe.db.exists("DocType", "With_Unique"):
			frappe.delete_doc("DocType", "With_Unique")

		dt = self.new_doctype("With_Unique", unique=1)
		dt.insert()

		doc1 = frappe.new_doc("With_Unique")
		doc2 = frappe.new_doc("With_Unique")
		doc1.some_fieldname = "Something"
		doc1.name = "one"
		doc2.some_fieldname = "Something"
		doc2.name = "two"

		doc1.insert()
		self.assertRaises(frappe.UniqueValidationError, doc2.insert)

		dt.fields[0].unique = 0
		dt.save()

		doc2.insert()
		doc1.delete()
		doc2.delete()

	def test_validate_search_fields(self):
		doc = self.new_doctype("Test Search Fields")
		doc.search_fields = "some_fieldname"
		doc.insert()
		self.assertEqual(doc.name, "Test Search Fields")

		# check if invalid fieldname is allowed or not
		doc.search_fields = "some_fieldname_1"
		self.assertRaises(frappe.ValidationError, doc.save)

		# check if no value fields are allowed in search fields
		field = doc.append("fields", {})
		field.fieldname = "some_html_field"
		field.fieldtype = "HTML"
		field.label = "Some HTML Field"
		doc.search_fields = "some_fieldname,some_html_field"
		self.assertRaises(frappe.ValidationError, doc.save)

	def test_depends_on_fields(self):
		doc = self.new_doctype("Test Depends On", depends_on="eval:doc.__islocal == 0")
		doc.insert()

		# check if the assignment operation is allowed in depends_on
		field = doc.fields[0]
		field.depends_on = "eval:doc.__islocal = 0"
		self.assertRaises(frappe.ValidationError, doc.save)

	def test_all_depends_on_fields_conditions(self):
		import re

		docfields = frappe.get_all("DocField", or_filters={
			"ifnull(depends_on, '')": ("!=", ''),
			"ifnull(collapsible_depends_on, '')": ("!=", '')
		}, fields=["parent", "depends_on", "collapsible_depends_on", "fieldname", "fieldtype"])

		pattern = """[\w\.:_]+\s*={1}\s*[\w\.@'"]+"""
		for field in docfields:
			for depends_on in ["depends_on", "collapsible_depends_on"]:
				condition = field.get(depends_on)
				if condition:
					self.assertFalse(re.match(pattern, condition))

	def test_unique_field_name_for_two_fields(self):
		doc = self.new_doctype('Test Unique Field')
		field_1 = doc.append('fields', {})
		field_1.fieldname  = 'some_fieldname_1'
		field_1.fieldtype = 'Data'

		field_2 = doc.append('fields', {})
		field_2.fieldname  = 'some_fieldname_1'
		field_2.fieldtype = 'Data'

		self.assertRaises(UniqueFieldnameError, doc.insert)

	def test_illegal_mandatory_validation(self):
		doc = self.new_doctype('Test Illegal mandatory')
		field_1 = doc.append('fields', {})
		field_1.fieldname  = 'some_fieldname_1'
		field_1.fieldtype = 'Section Break'
		field_1.reqd = 1

		self.assertRaises(IllegalMandatoryError, doc.insert)

	def test_link_with_wrong_and_no_options(self):
		doc = self.new_doctype('Test link')
		field_1 = doc.append('fields', {})
		field_1.fieldname  = 'some_fieldname_1'
		field_1.fieldtype = 'Link'

		self.assertRaises(DoctypeLinkError, doc.insert)

		field_1.options = 'wrongdoctype'

		self.assertRaises(WrongOptionsDoctypeLinkError, doc.insert)

	def test_hidden_and_mandatory_without_default(self):
		doc = self.new_doctype('Test hidden and mandatory')
		field_1 = doc.append('fields', {})
		field_1.fieldname  = 'some_fieldname_1'
		field_1.fieldtype = 'Data'
		field_1.reqd = 1
		field_1.hidden = 1

		self.assertRaises(HiddenAndMandatoryWithoutDefaultError, doc.insert)

	def test_field_can_not_be_indexed_validation(self):
		doc = self.new_doctype('Test index')
		field_1 = doc.append('fields', {})
		field_1.fieldname  = 'some_fieldname_1'
		field_1.fieldtype = 'Long Text'
		field_1.search_index = 1

		self.assertRaises(CannotIndexedError, doc.insert)