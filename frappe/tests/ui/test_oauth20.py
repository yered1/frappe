# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt
from __future__ import unicode_literals

import unittest, frappe, requests, time
from frappe.test_runner import make_test_records
from frappe.utils.selenium_testdriver import TestDriver
from six.moves.urllib.parse import urlparse, parse_qs

class TestOAuth20(unittest.TestCase):
	def setUp(self):
		self.driver = TestDriver()
		make_test_records("OAuth Client")
		make_test_records("User")
		self.client_id = frappe.get_all("OAuth Client", fields=["*"])[0].get("client_id")

		# Set Frappe server URL reqired for id_token generation
		try:
			frappe_login_key = frappe.get_doc("Social Login Key", "frappe")
		except frappe.DoesNotExistError:
			frappe_login_key = frappe.new_doc("Social Login Key")
		frappe_login_key.get_social_login_provider("Frappe", initialize=True)
		frappe_login_key.base_url = "http://localhost:8000"
		frappe_login_key.enable_social_login = 0
		frappe_login_key.save()

	def test_invalid_login(self):
		self.assertFalse(check_valid_openid_response())

	def test_login_using_authorization_code(self):

		# Go to Authorize url
		self.driver.get(
			"api/method/frappe.integrations.oauth2.authorize?client_id=" +
			self.client_id +
			"&scope=all%20openid&response_type=code&redirect_uri=http%3A%2F%2Flocalhost"
		)

		time.sleep(2)

		# Login
		username = self.driver.find("#login_email")[0]
		username.send_keys("test@example.com")

		password = self.driver.find("#login_password")[0]
		password.send_keys("Eastern_43A1W")

		sign_in = self.driver.find(".btn-login")[0]
		sign_in.submit()

		time.sleep(2)

		# Allow access to resource
		allow = self.driver.find("#allow")[0]
		allow.click()

		time.sleep(2)

		# Get authorization code from redirected URL
		auth_code = urlparse(self.driver.driver.current_url).query.split("=")[1]

		payload = "grant_type=authorization_code&code="
		payload += auth_code
		payload += "&redirect_uri=http%3A%2F%2Flocalhost&client_id="
		payload += self.client_id

		headers = {'content-type':'application/x-www-form-urlencoded'}

		# Request for bearer token
		token_response = requests.post( frappe.get_site_config().host_name +
			"/api/method/frappe.integrations.oauth2.get_token", data=payload, headers=headers)

		# Parse bearer token json
		bearer_token = token_response.json()

		self.assertTrue(bearer_token.get("access_token"))
		self.assertTrue(bearer_token.get("expires_in"))
		self.assertTrue(bearer_token.get("id_token"))
		self.assertTrue(bearer_token.get("refresh_token"))
		self.assertTrue(bearer_token.get("scope"))
		self.assertTrue(bearer_token.get("token_type") == "Bearer")
		self.assertTrue(check_valid_openid_response(bearer_token.get("access_token")))

		# Revoke Token
		revoke_token_response = requests.post(frappe.get_site_config().host_name + "/api/method/frappe.integrations.oauth2.revoke_token",
			data="token=" + bearer_token.get("access_token"))
		self.assertTrue(revoke_token_response.status_code == 200)

		# Check revoked token
		self.assertFalse(check_valid_openid_response(bearer_token.get("access_token")))

	def test_resource_owner_password_credentials_grant(self):
		# Set payload
		payload = "grant_type=password"
		payload += "&username=test@example.com"
		payload += "&password=Eastern_43A1W"
		payload += "&client_id=" + self.client_id
		payload += "&scope=openid%20all"

		headers = {'content-type':'application/x-www-form-urlencoded'}

		# Request for bearer token
		token_response = requests.post( frappe.get_site_config().host_name +
			"/api/method/frappe.integrations.oauth2.get_token", data=payload, headers=headers)

		# Parse bearer token json
		bearer_token = token_response.json()

		# Check token for valid response
		self.assertTrue(check_valid_openid_response(bearer_token.get("access_token")))

	def test_login_using_implicit_token(self):

		oauth_client = frappe.get_doc("OAuth Client", self.client_id)
		oauth_client.grant_type = "Implicit"
		oauth_client.response_type = "Token"
		oauth_client.save()
		frappe.db.commit()

		# Go to Authorize url
		self.driver.get(
			"api/method/frappe.integrations.oauth2.authorize?client_id=" +
			self.client_id +
			"&scope=all%20openid&response_type=token&redirect_uri=http%3A%2F%2Flocalhost"
		)

		time.sleep(2)

		# Login
		username = self.driver.find("#login_email")[0]
		username.send_keys("test@example.com")

		password = self.driver.find("#login_password")[0]
		password.send_keys("Eastern_43A1W")

		sign_in = self.driver.find(".btn-login")[0]
		sign_in.submit()

		time.sleep(2)

		# Allow access to resource
		allow = self.driver.find("#allow")[0]
		allow.click()

		time.sleep(2)

		# Get token from redirected URL
		response_url = dict(parse_qs(urlparse(self.driver.driver.current_url).fragment))

		self.assertTrue(response_url.get("access_token"))
		self.assertTrue(response_url.get("expires_in"))
		self.assertTrue(response_url.get("scope"))
		self.assertTrue(response_url.get("token_type"))
		self.assertTrue(check_valid_openid_response(response_url.get("access_token")))

	def tearDown(self):
		self.driver.close()

def check_valid_openid_response(access_token=None):
	# Returns True for valid response

	# Use token in header
	headers = {}
	if access_token:
		headers["Authorization"] = 'Bearer' + access_token

	# check openid for email test@example.com
	openid_response = requests.get(frappe.get_site_config().host_name +
		"/api/method/frappe.integrations.oauth2.openid_profile", headers=headers)

	return True if openid_response.status_code == 200 else False
