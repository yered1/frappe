from __future__ import unicode_literals
from . import __version__ as app_version


app_name = "frappe"
app_title = "Frappe Framework"
app_publisher = "Frappe Technologies"
app_description = "Full stack web framework with Python, Javascript, MariaDB, Redis, Node"
app_icon = "octicon octicon-circuit-board"
app_color = "orange"
source_link = "https://github.com/frappe/frappe"
app_license = "MIT"

develop_version = '12.x.x-develop'

app_email = "info@frappe.io"

docs_app = "frappe_io"

before_install = "frappe.utils.install.before_install"
after_install = "frappe.utils.install.after_install"

page_js = {
	"setup-wizard": "public/js/frappe/setup_wizard.js"
}

# website
app_include_js = [
	"assets/js/libs.min.js",
	"assets/js/desk.min.js",
	"assets/js/list.min.js",
	"assets/js/form.min.js",
	"assets/js/control.min.js",
	"assets/js/report.min.js",
	"assets/frappe/js/frappe/toolbar.js"
]
app_include_css = [
	"assets/css/desk.min.css",
	"assets/css/list.min.css",
	"assets/css/form.min.css",
	"assets/css/report.min.css",
	"assets/css/module.min.css"
]

web_include_js = [
	"website_script.js"
]

web_include_css = []

website_route_rules = [
	{"from_route": "/blog/<category>", "to_route": "Blog Post"},
	{"from_route": "/kb/<category>", "to_route": "Help Article"},
	{"from_route": "/newsletters", "to_route": "Newsletter"},
	{"from_route": "/profile", "to_route": "me"},
]

write_file_keys = ["file_url", "file_name"]

notification_config = "frappe.core.notifications.get_notification_config"

before_tests = "frappe.utils.install.before_tests"

email_append_to = ["Event", "ToDo", "Communication"]

get_rooms = 'frappe.chat.doctype.chat_room.chat_room.get_rooms'

calendars = ["Event"]

# login

on_session_creation = [
	"frappe.core.doctype.activity_log.feed.login_feed",
	"frappe.core.doctype.user.user.notify_admin_access_to_system_manager",
	"frappe.limits.check_if_expired",
	"frappe.utils.scheduler.reset_enabled_scheduler_events",
]

# permissions

permission_query_conditions = {
	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
	"ToDo": "frappe.desk.doctype.todo.todo.get_permission_query_conditions",
	"User": "frappe.core.doctype.user.user.get_permission_query_conditions",
	"Note": "frappe.desk.doctype.note.note.get_permission_query_conditions",
	"Kanban Board": "frappe.desk.doctype.kanban_board.kanban_board.get_permission_query_conditions",
	"Contact": "frappe.contacts.address_and_contact.get_permission_query_conditions_for_contact",
	"Address": "frappe.contacts.address_and_contact.get_permission_query_conditions_for_address",
	"Communication": "frappe.core.doctype.communication.communication.get_permission_query_conditions_for_communication",
	"Workflow Action": "frappe.workflow.doctype.workflow_action.workflow_action.get_permission_query_conditions"
}

has_permission = {
	"Event": "frappe.desk.doctype.event.event.has_permission",
	"ToDo": "frappe.desk.doctype.todo.todo.has_permission",
	"User": "frappe.core.doctype.user.user.has_permission",
	"Note": "frappe.desk.doctype.note.note.has_permission",
	"Kanban Board": "frappe.desk.doctype.kanban_board.kanban_board.has_permission",
	"Contact": "frappe.contacts.address_and_contact.has_permission",
	"Address": "frappe.contacts.address_and_contact.has_permission",
	"Communication": "frappe.core.doctype.communication.communication.has_permission",
	"Workflow Action": "frappe.workflow.doctype.workflow_action.workflow_action.has_permission",
	"File": "frappe.core.doctype.file.file.has_permission"
}

has_website_permission = {
	"Address": "frappe.contacts.doctype.address.address.has_website_permission"
}

standard_queries = {
	"User": "frappe.core.doctype.user.user.user_query"
}

doc_events = {
	"*": {
		"on_update": [
			"frappe.desk.notifications.clear_doctype_notifications",
			"frappe.core.doctype.activity_log.feed.update_feed",
			"frappe.workflow.doctype.workflow_action.workflow_action.process_workflow_actions",
			"frappe.automation.doctype.assignment_rule.assignment_rule.apply",
			"frappe.automation.doctype.milestone_tracker.milestone_tracker.evaluate_milestone"
		],
		"after_rename": "frappe.desk.notifications.clear_doctype_notifications",
		"on_cancel": [
			"frappe.desk.notifications.clear_doctype_notifications",
			"frappe.workflow.doctype.workflow_action.workflow_action.process_workflow_actions"
		],
		"on_trash": [
			"frappe.desk.notifications.clear_doctype_notifications",
			"frappe.workflow.doctype.workflow_action.workflow_action.process_workflow_actions"
		],
		"on_change": [
			"frappe.social.doctype.energy_point_rule.energy_point_rule.process_energy_points"
		],
	},
	"Email Group Member": {
		"validate": "frappe.email.doctype.email_group.email_group.restrict_email_group"
	}
}

scheduler_events = {
	"all": [
		"frappe.email.queue.flush",
		"frappe.email.doctype.email_account.email_account.pull",
		"frappe.email.doctype.email_account.email_account.notify_unreplied",
		"frappe.oauth.delete_oauth2_data",
		"frappe.integrations.doctype.razorpay_settings.razorpay_settings.capture_payment",
		"frappe.twofactor.delete_all_barcodes_for_users",
		"frappe.integrations.doctype.gcalendar_settings.gcalendar_settings.sync",
		"frappe.website.doctype.web_page.web_page.check_publish_status",
		'frappe.utils.global_search.sync_global_search'
	],
	"hourly": [
		"frappe.model.utils.link_count.update_link_count",
		'frappe.model.utils.user_settings.sync_user_settings',
		"frappe.utils.error.collect_error_snapshots",
		"frappe.desk.page.backups.backups.delete_downloadable_backups",
		"frappe.limits.update_space_usage",
		"frappe.limits.update_site_usage",
		"frappe.desk.doctype.auto_repeat.auto_repeat.make_auto_repeat_entry",
		"frappe.deferred_insert.save_to_db",
		"frappe.desk.form.document_follow.send_hourly_updates"
	],
	"daily": [
		"frappe.email.queue.clear_outbox",
		"frappe.desk.notifications.clear_notifications",
		"frappe.core.doctype.error_log.error_log.set_old_logs_as_seen",
		"frappe.desk.doctype.event.event.send_event_digest",
		"frappe.sessions.clear_expired_sessions",
		"frappe.email.doctype.notification.notification.trigger_daily_alerts",
		"frappe.realtime.remove_old_task_logs",
		"frappe.utils.scheduler.disable_scheduler_on_expiry",
		"frappe.utils.scheduler.restrict_scheduler_events_if_dormant",
		"frappe.email.doctype.auto_email_report.auto_email_report.send_daily",
		"frappe.core.doctype.activity_log.activity_log.clear_authentication_logs",
		"frappe.website.doctype.personal_data_deletion_request.personal_data_deletion_request.remove_unverified_record",
		"frappe.desk.form.document_follow.send_daily_updates",
		"frappe.social.doctype.energy_point_settings.energy_point_settings.allocate_review_points"
	],
	"daily_long": [
		"frappe.integrations.doctype.dropbox_settings.dropbox_settings.take_backups_daily",
		"frappe.integrations.doctype.s3_backup_settings.s3_backup_settings.take_backups_daily"
	],
	"weekly_long": [
		"frappe.integrations.doctype.dropbox_settings.dropbox_settings.take_backups_weekly",
		"frappe.integrations.doctype.s3_backup_settings.s3_backup_settings.take_backups_weekly",
		"frappe.utils.change_log.check_for_update",
		"frappe.desk.doctype.route_history.route_history.flush_old_route_records",
		"frappe.desk.form.document_follow.send_weekly_updates",
		"frappe.social.doctype.energy_point_log.energy_point_log.send_weekly_summary"
	],
	"monthly": [
		"frappe.email.doctype.auto_email_report.auto_email_report.send_monthly",
		"frappe.social.doctype.energy_point_log.energy_point_log.send_monthly_summary"
	],
	"monthly_long": [
		"frappe.integrations.doctype.s3_backup_settings.s3_backup_settings.take_backups_monthly"
	]
}

get_translated_dict = {
	("doctype", "System Settings"): "frappe.geo.country_info.get_translated_dict",
	("page", "setup-wizard"): "frappe.geo.country_info.get_translated_dict"
}

sounds = [
	{"name": "email", "src": "/assets/frappe/sounds/email.mp3", "volume": 0.1},
	{"name": "submit", "src": "/assets/frappe/sounds/submit.mp3", "volume": 0.1},
	{"name": "cancel", "src": "/assets/frappe/sounds/cancel.mp3", "volume": 0.1},
	{"name": "delete", "src": "/assets/frappe/sounds/delete.mp3", "volume": 0.05},
	{"name": "click", "src": "/assets/frappe/sounds/click.mp3", "volume": 0.05},
	{"name": "error", "src": "/assets/frappe/sounds/error.mp3", "volume": 0.1},
	{"name": "alert", "src": "/assets/frappe/sounds/alert.mp3", "volume": 0.2},
	# {"name": "chime", "src": "/assets/frappe/sounds/chime.mp3"},

	# frappe.chat sounds
	{ "name": "chat-message", 	   "src": "/assets/frappe/sounds/chat-message.mp3",      "volume": 0.1 },
	{ "name": "chat-notification", "src": "/assets/frappe/sounds/chat-notification.mp3", "volume": 0.1 }
	# frappe.chat sounds
]

bot_parsers = [
	'frappe.utils.bot.ShowNotificationBot',
	'frappe.utils.bot.GetOpenListBot',
	'frappe.utils.bot.ListBot',
	'frappe.utils.bot.FindBot',
	'frappe.utils.bot.CountBot'
]

setup_wizard_exception = "frappe.desk.page.setup_wizard.setup_wizard.email_setup_wizard_exception"
before_write_file = "frappe.limits.validate_space_limit"

before_migrate = ['frappe.patches.v11_0.sync_user_permission_doctype_before_migrate.execute']

otp_methods = ['OTP App','Email','SMS']
user_privacy_documents = [
	{
		'doctype': 'File',
		'match_field': 'attached_to_name',
		'personal_fields': ['file_name', 'file_url'],
		'applies_to_website_user': 1
	},
	{
		'doctype': 'Email Group Member',
		'match_field': 'email',
	},
	{
		'doctype': 'Email Unsubscribe',
		'match_field': 'email',
	},
	{
		'doctype': 'Email Queue',
		'match_field': 'sender',
	},
	{
		'doctype': 'Email Queue Recipient',
		'match_field': 'recipient',
	},
	{
		'doctype': 'Contact',
		'match_field': 'email_id',
		'personal_fields': ['first_name', 'last_name', 'phone', 'mobile_no'],
	},
	{
		'doctype': 'Address',
		'match_field': 'email_id',
		'personal_fields': ['address_title', 'address_line1', 'address_line2', 'city', 'county', 'state', 'pincode',
			'phone', 'fax'],
	},
	{
		'doctype': 'Communication',
		'match_field': 'sender',
		'personal_fields': ['sender_full_name', 'phone_no', 'content'],
	},
	{
		'doctype': 'Communication',
		'match_field': 'recipients',
	},
	{
		'doctype': 'User',
		'match_field': 'name',
		'personal_fields': ['email', 'username', 'first_name', 'middle_name', 'last_name', 'full_name', 'birth_date',
			'user_image', 'phone', 'mobile_no', 'location', 'banner_image', 'interest', 'bio', 'email_signature', 'background_image'],
		'applies_to_website_user': 1
	},

]
