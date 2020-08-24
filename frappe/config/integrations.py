from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			"label": _("Payments"),
			"icon": "fa fa-star",
			"items": [
				{
					"type": "doctype",
					"name": "Braintree Settings",
					"description": _("Braintree payment gateway settings"),
				},
				{
					"type": "doctype",
					"name": "PayPal Settings",
					"description": _("PayPal payment gateway settings"),
				},
				{
					"type": "doctype",
					"name": "Razorpay Settings",
					"description": _("Razorpay Payment gateway settings"),
				},
				{
					"type": "doctype",
					"name": "Stripe Settings",
					"description": _("Stripe payment gateway settings"),
				},
			]
		},
		{
			"label": _("Backup"),
			"items": [
				{
					"type": "doctype",
					"name": "Dropbox Settings",
					"description": _("Dropbox backup settings"),
				},
				{
					"type": "doctype",
					"name": "S3 Backup Settings",
					"description": _("S3 Backup Settings"),
				},
			]
		},
		{
			"label": _("Authentication"),
			"items": [
				{
					"type": "doctype",
					"name": "Social Login Key",
					"description": _("Enter keys to enable login via Facebook, Google, GitHub."),
				},
				{
					"type": "doctype",
					"name": "LDAP Settings",
					"description": _("Ldap settings"),
				},
				{
					"type": "doctype",
					"name": "OAuth Client",
					"description": _("Register OAuth Client App"),
				},
				{
					"type": "doctype",
					"name": "OAuth Provider Settings",
					"description": _("Settings for OAuth Provider"),
				},
			]
		},
		{
			"label": _("Webhook"),
			"items": [
				{
					"type": "doctype",
					"name": "Webhook",
					"description": _("Webhooks calling API requests into web apps"),
				},
				{
					"type": "doctype",
					"name": "Slack Webhook URL",
					"description": _("Slack Webhooks for internal integration"),
				},
			]
		},
		{
			"label": _("Google Services"),
			"items": [
				{
					"type": "doctype",
					"name": "Google Maps Settings",
					"description": _("Google Maps integration"),
				},
				{
					"type": "doctype",
					"name": "GCalendar Settings",
					"description": _("Configure your google calendar integration"),
				},
				{
					"type": "doctype",
					"name": "GCalendar Account",
					"description": _("Configure accounts for google calendar"),
				},
				{
					"type": "doctype",
					"name": "GSuite Settings",
					"description": _("Enter keys to enable integration with Google GSuite"),
				},
				{
					"type": "doctype",
					"name": "GSuite Templates",
					"description": _("Google GSuite Templates to integration with DocTypes"),
				}
			]
		}
	]
