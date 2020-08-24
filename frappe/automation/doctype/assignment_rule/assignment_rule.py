# -*- coding: utf-8 -*-
# Copyright (c) 2019, Frappe Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import frappe
from frappe.model.document import Document
from frappe.desk.form import assign_to
import frappe.cache_manager

class AssignmentRule(Document):
	def on_update(self): # pylint: disable=no-self-use
		frappe.cache_manager.clear_doctype_map('Assignment Rule', self.name)

	def after_rename(self): # pylint: disable=no-self-use
		frappe.cache_manager.clear_doctype_map('Assignment Rule', self.name)

	def apply_unassign(self, doc, assignments):
		if (self.unassign_condition and
			self.name in [d.assignment_rule for d in assignments]):
			return self.clear_assignment(doc)

		return False

	def apply_assign(self, doc):
		if self.safe_eval('assign_condition', doc):
			self.do_assignment(doc)
			return True


	def do_assignment(self, doc):
		# clear existing assignment, to reassign
		assign_to.clear(doc.get('doctype'), doc.get('name'))

		user = self.get_user()

		assign_to.add(dict(
			assign_to = user,
			doctype = doc.get('doctype'),
			name = doc.get('name'),
			description = frappe.render_template(self.description, doc),
			assignment_rule = self.name
		))

		# set for reference in round robin
		self.db_set('last_user', user)

	def clear_assignment(self, doc):
		'''Clear assignments'''
		if self.safe_eval('unassign_condition', doc):
			return assign_to.clear(doc.get('doctype'), doc.get('name'))

	def get_user(self):
		'''
		Get the next user for assignment
		'''
		if self.rule == 'Round Robin':
			return self.get_user_round_robin()
		elif self.rule == 'Load Balancing':
			return self.get_user_load_balancing()

	def get_user_round_robin(self):
		'''
		Get next user based on round robin
		'''

		# first time, or last in list, pick the first
		if not self.last_user or self.last_user == self.users[-1].user:
			return self.users[0].user

		# find out the next user in the list
		for i, d in enumerate(self.users):
			if self.last_user == d.user:
				return self.users[i+1].user

		# bad last user, assign to the first one
		return self.users[0].user

	def get_user_load_balancing(self):
		'''Assign to the user with least number of open assignments'''
		counts = []
		for d in self.users:
			counts.append(dict(
				user = d.user,
				count = frappe.db.count('ToDo', dict(
					reference_type = self.document_type,
					owner = d.user,
					status = "Open"))
			))

		# sort by dict value
		sorted_counts = sorted(counts, key = lambda k: k['count'])

		# pick the first user
		return sorted_counts[0].get('user')

	def safe_eval(self, fieldname, doc):
		try:
			return frappe.safe_eval(self.get(fieldname), None, doc)
		except Exception as e:
			# when assignment fails, don't block the document as it may be
			# a part of the email pulling
			frappe.msgprint(frappe._('Auto assignment failed: {0}').format(str(e)), indicator = 'orange')

def get_assignments(doc):
	return frappe.get_all('ToDo', fields = ['name', 'assignment_rule'], filters = dict(
		reference_type = doc.get('doctype'),
		reference_name = doc.get('name'),
		status = 'Open'
	), limit = 5)

def apply(doc, method):
	if frappe.flags.in_patch or frappe.flags.in_install:
		return

	assignment_rules = frappe.cache_manager.get_doctype_map('Assignment Rule', doc.doctype, dict(
		document_type = doc.doctype, disabled = 0), order_by = 'priority desc')

	assignment_rule_docs = []

	# multiple auto assigns
	for d in assignment_rules:
		assignment_rule_docs.append(frappe.get_doc('Assignment Rule', d.name))

	if not assignment_rule_docs:
		return

	doc = doc.as_dict()
	assignments = get_assignments(doc)

	clear = True
	if assignments:
		# first unassign
		clear = False
		for assignment_rule in assignment_rule_docs:
			clear = assignment_rule.apply_unassign(doc, assignments)
			if clear: break

	# apply rule only if there are no exisiting assignments
	if clear:
		for assignment_rule in assignment_rule_docs:
			if assignment_rule.apply_assign(doc): break


def get_assignment_rules():
	return [d.document_type for d in frappe.db.get_all('Assignment Rule', fields=['document_type'], filters=dict(disabled = 0))]