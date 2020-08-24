# -*- coding: utf-8 -*-
# Copyright (c) 2017, Frappe Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe, json
from frappe.model.document import Document
from frappe.permissions import (get_valid_perms, update_permission_property)
from frappe import _
from frappe.core.utils import find
from frappe.desk.form.linked_with import get_linked_doctypes

class UserPermission(Document):
	def validate(self):
		duplicate_exists = frappe.db.get_all(self.doctype, filters={
			'allow': self.allow,
			'for_value': self.for_value,
			'user': self.user,
			'applicable_for': self.applicable_for,
			'apply_to_all_doctypes': self.apply_to_all_doctypes,
			'name': ['!=', self.name]
		}, limit=1)
		if duplicate_exists:
			frappe.throw(_("User permission already exists"), frappe.DuplicateEntryError)

	def on_update(self):
		frappe.cache().delete_value('user_permissions')
		frappe.publish_realtime('update_user_permissions')

	def on_trash(self): # pylint: disable=no-self-use
		frappe.cache().delete_value('user_permissions')
		frappe.publish_realtime('update_user_permissions')

@frappe.whitelist()
def get_user_permissions(user=None):
	'''Get all users permissions for the user as a dict of doctype'''
	# if this is called from client-side,
	# user can access only his/her user permissions
	if frappe.request and frappe.local.form_dict.cmd == 'get_user_permissions':
		user = frappe.session.user

	if not user:
		user = frappe.session.user

	if user == "Administrator":
		return {}

	cached_user_permissions = frappe.cache().hget("user_permissions", user)

	if cached_user_permissions is not None:
		return cached_user_permissions

	out = {}

	def add_doc_to_perm(perm, doc_name):
		# group rules for each type
		# for example if allow is "Customer", then build all allowed customers
		# in a list
		if not out.get(perm.allow):
			out[perm.allow] = []

		out[perm.allow].append(frappe._dict({
			'doc': doc_name,
			'applicable_for': perm.get('applicable_for')
		}))

	try:
		for perm in frappe.get_all('User Permission',
			fields=['allow', 'for_value', 'applicable_for'],
			filters=dict(user=user)):

			meta = frappe.get_meta(perm.allow)
			add_doc_to_perm(perm, perm.for_value)

			if meta.is_nested_set():
				decendants = frappe.db.get_descendants(perm.allow, perm.for_value)
				for doc in decendants:
					add_doc_to_perm(perm, doc)

		out = frappe._dict(out)
		frappe.cache().hset("user_permissions", user, out)

	except frappe.SQLError as e:
		if e.args[0]==1146:
			# called from patch
			pass

	return out

def user_permission_exists(user, allow, for_value, applicable_for=None):
	'''Checks if similar user permission already exists'''
	user_permissions = get_user_permissions(user).get(allow, [])
	if not user_permissions: return None
	has_same_user_permission = find(user_permissions, lambda perm:perm["doc"] == for_value and perm.get('applicable_for') == applicable_for)

	return has_same_user_permission

def get_applicable_for_doctype_list(doctype, txt, searchfield, start, page_len, filters):
	linked_doctypes = get_linked_doctypes(doctype, True).keys()
	linked_doctypes = list(linked_doctypes)
	linked_doctypes += [doctype]

	if txt:
		linked_doctypes = [d for d in linked_doctypes if txt in d.lower()]

	linked_doctypes.sort()

	return_list = []
	for doctype in linked_doctypes[start:page_len]:
		return_list.append([doctype])

	return return_list

def get_permitted_documents(doctype):
	return [d.get('doc') for d in get_user_permissions().get(doctype, []) \
		if d.get('doc')]

@frappe.whitelist()
def check_applicable_doc_perm(user, doctype, docname):
	frappe.only_for('System Manager')
	applicable = []
	doc_exists = frappe.get_all('User Permission',
		fields=['name'],
		filters={"user": user,
			"allow": doctype,
			"for_value": docname,
			"apply_to_all_doctypes":1,
		}, limit=1)
	if doc_exists:
		applicable = get_linked_doctypes(doctype).keys()
	else:
		data = frappe.get_all('User Permission',
			fields=['applicable_for'],
			filters={"user": user,
				"allow": doctype,
				"for_value":docname,
			})
		for d in data:
			applicable.append(d.applicable_for)
	return applicable


@frappe.whitelist()
def clear_user_permissions(user, for_doctype):
	frappe.only_for('System Manager')
	total = frappe.db.count('User Permission', filters = dict(user=user, allow=for_doctype))
	if total:
		frappe.db.sql('DELETE FROM `tabUser Permission` WHERE user=%s AND allow=%s', (user, for_doctype))
		frappe.clear_cache()
	return total

@frappe.whitelist()
def add_user_permissions(data):
	''' Add and update the user permissions '''
	frappe.only_for('System Manager')
	if isinstance(data, frappe.string_types):
		data = json.loads(data)
	data = frappe._dict(data)

	d = check_applicable_doc_perm(data.user, data.doctype, data.docname)
	exists = frappe.db.exists("User Permission", {
		"user": data.user,
		"allow": data.doctype,
		"for_value": data.docname,
		"apply_to_all_doctypes": 1
	})
	if data.apply_to_all_doctypes == 1 and not exists:
		remove_applicable(d, data.user, data.doctype, data.docname)
		insert_user_perm(data.user, data.doctype, data.docname, apply_to_all = 1)
		return 1
	elif len(data.applicable_doctypes) > 0 and data.apply_to_all_doctypes != 1:
		remove_apply_to_all(data.user, data.doctype, data.docname)
		update_applicable(d, data.applicable_doctypes, data.user, data.doctype, data.docname)
		for applicable in data.applicable_doctypes :
			if applicable not in d:
				insert_user_perm(data.user, data.doctype, data.docname, applicable = applicable)
			elif exists:
				insert_user_perm(data.user, data.doctype, data.docname, applicable = applicable)
		return 1
	return 0

def insert_user_perm(user, doctype, docname, apply_to_all=None, applicable=None):
	user_perm = frappe.new_doc("User Permission")
	user_perm.user = user
	user_perm.allow = doctype
	user_perm.for_value = docname
	if applicable:
		user_perm.applicable_for  = applicable
		user_perm.apply_to_all_doctypes = 0
	else:
		user_perm.apply_to_all_doctypes = 1
	user_perm.insert()

def remove_applicable(d, user, doctype, docname):
	for applicable_for in d:
		frappe.db.sql("""DELETE FROM `tabUser Permission`
			WHERE `user`=%s
			AND `applicable_for`=%s
			AND `allow`=%s
			AND `for_value`=%s
		""", (user, applicable_for, doctype, docname))

def remove_apply_to_all(user, doctype, docname):
	frappe.db.sql("""DELETE from `tabUser Permission`
		WHERE `user`=%s
		AND `apply_to_all_doctypes`=1
		AND `allow`=%s
		AND `for_value`=%s
	""",(user, doctype, docname))

def update_applicable(already_applied, to_apply, user, doctype, docname):
	for applied in already_applied:
		if applied not in to_apply:
			frappe.db.sql("""DELETE FROM `tabUser Permission`
				WHERE `user`=%s
				AND `applicable_for`=%s
				AND `allow`=%s
				AND `for_value`=%s
			""",(user, applied, doctype, docname))