# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document

class WebsiteTheme(Document):
	def validate(self):
		self.validate_if_customizable()
		self.validate_theme()

	def on_update(self):
		if (not self.custom
			and frappe.local.conf.get('developer_mode')
			and not (frappe.flags.in_import or frappe.flags.in_test)):

			self.export_doc()

		self.clear_cache_if_current_theme()

	def is_standard_and_not_valid_user(self):
		return (not self.custom
			and not frappe.local.conf.get('developer_mode')
			and not (frappe.flags.in_import or frappe.flags.in_test))

	def on_trash(self):
		if self.is_standard_and_not_valid_user():
			frappe.throw(_("You are not allowed to delete a standard Website Theme"),
				frappe.PermissionError)

	def validate_if_customizable(self):
		if self.is_standard_and_not_valid_user():
			frappe.throw(_("Please Duplicate this Website Theme to customize."))

	def validate_theme(self):
		'''Generate theme css if theme_scss has changed'''
		if self.theme_scss:
			doc_before_save = self.get_doc_before_save()
			if doc_before_save is None or self.theme_scss != doc_before_save.theme_scss:
				self.generate_bootstrap_theme()

	def export_doc(self):
		"""Export to standard folder `[module]/website_theme/[name]/[name].json`."""
		from frappe.modules.export_file import export_to_files
		export_to_files(record_list=[['Website Theme', self.name]], create_init=True)


	def clear_cache_if_current_theme(self):
		if frappe.flags.in_install == 'frappe': return
		website_settings = frappe.get_doc("Website Settings", "Website Settings")
		if getattr(website_settings, "website_theme", None) == self.name:
			website_settings.clear_cache()

	def generate_bootstrap_theme(self):
		from subprocess import Popen, PIPE
		from os.path import join as join_path

		file_name = frappe.scrub(self.name) + '_' + frappe.generate_hash('Website Theme', 8) + '.css'
		output_path = join_path(frappe.utils.get_bench_path(), 'sites', 'assets', 'css', file_name)
		content = self.theme_scss
		content = content.replace('\n', '\\n')
		command = ['node', 'generate_bootstrap_theme.js', output_path, content]

		process = Popen(command, cwd=frappe.get_app_path('frappe', '..'), stdout=PIPE, stderr=PIPE)

		stderr = process.communicate()[1]

		if stderr:
			frappe.throw('<pre>{stderr}</pre>'.format(stderr=frappe.safe_encode(stderr)))
		else:
			self.theme_url = '/assets/css/' + file_name

		frappe.msgprint(_('Compiled Successfully'), alert=True)

	def use_theme(self):
		use_theme(self.name)

@frappe.whitelist()
def use_theme(theme):
	website_settings = frappe.get_doc("Website Settings", "Website Settings")
	website_settings.website_theme = theme
	website_settings.ignore_validate = True
	website_settings.save()

def add_website_theme(context):
	context.theme = frappe._dict()

	if not context.disable_website_theme:
		website_theme = get_active_theme()
		context.theme = website_theme and website_theme.as_dict() or frappe._dict()

def get_active_theme():
	website_theme = frappe.db.get_value("Website Settings", "Website Settings", "website_theme")
	if website_theme:
		try:
			return frappe.get_doc("Website Theme", website_theme)
		except frappe.DoesNotExistError:
			pass
