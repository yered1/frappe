# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals

import frappe
from frappe.model.document import get_controller
from frappe.utils import get_request_site_address, get_datetime, nowdate
from frappe.website.router import get_pages, get_all_page_context_from_doctypes
from six import iteritems
from six.moves.urllib.parse import quote, urljoin

no_cache = 1
base_template_path = "templates/www/sitemap.xml"

def get_context(context):
	"""generate the sitemap XML"""
	host = get_request_site_address()
	links = []
	for route, page in iteritems(get_pages()):
		if page.sitemap:
			links.append({
				"loc": urljoin(host, quote(page.name.encode("utf-8"))),
				"lastmod": nowdate()
			})

	for route, data in iteritems(get_public_pages_from_doctypes()):
		links.append({
			"loc": urljoin(host, quote((route or "").encode("utf-8"))),
			"lastmod": get_datetime(data.get("modified")).strftime("%Y-%m-%d")
		})

	return {"links":links}

def get_public_pages_from_doctypes():
	'''Returns pages from doctypes that are publicly accessible'''

	def get_sitemap_routes():
		routes = {}
		doctypes_with_web_view = [d.name for d in frappe.db.get_all('DocType', {
			'has_web_view': 1,
			'allow_guest_to_view': 1
		})]

		for doctype in doctypes_with_web_view:
			controller = get_controller(doctype)
			meta = frappe.get_meta(doctype)
			condition_field = meta.is_published_field or controller.website.condition_field

			try:
				res = frappe.db.get_all(doctype, ['route', 'name', 'modified'], { condition_field: 1 })
				for r in res:
					routes[r.route] = {"doctype": doctype, "name": r.name, "modified": r.modified}

			except Exception as e:
				if not frappe.db.is_missing_column(e): raise e

		return routes

	return frappe.cache().get_value("sitemap_routes", get_sitemap_routes)
