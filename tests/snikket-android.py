#!/usr/bin/env python3

from appium import webdriver
from selenium.webdriver.support.ui import WebDriverWait as wait

import requests
import random, string, base64
import http, urllib
from collections import namedtuple
import argparse
try:
    import json
except ImportError:
    import simplejson as json

parser = argparse.ArgumentParser(
	description="Run Appium tests of an XMPP client",
	epilog= """Capabilities (aka 'caps') specify the session configuration. Multiple
caps options may be specified, they are processed in order, with later options overriding
earlier options in case of duplicate keys."""
)

parser.add_argument("domain", help="The domain name of the server to connect to")
parser.add_argument("invite_key", help="An API key used to create invites")
parser.add_argument("--driver-url", help="Base URL of the driver API", default="http://localhost:4723/wd/hub")
parser.add_argument("--report-url", help="URL to report result to")
parser.add_argument("--caps-file", help="Add caps from JSON file", action='append', dest='caps_files')
parser.add_argument("--cap", help="Specify a single capability entry (e.g. foo=bar)", action='append', dest='caps')
args = parser.parse_args()

base_url = args.driver_url
invite_key = args.invite_key

caps = {}

if args.caps_files:
	for caps_filename in args.caps_files:
		with open(caps_filename, 'r') as caps_file:
			new_caps = json.loads(caps_file.read())
			for cap_name in new_caps:
				caps[cap_name] = new_caps[cap_name]

if args.caps:
	for cap_entry in args.caps:
		s = cap_entry.split("=", 2)
		caps[s[0]] = s[1]

def randomword(length):
	letters = string.ascii_lowercase
	return ''.join(random.choice(letters) for i in range(length))

def get_invite_uri():
	r = requests.get("https://%s/invites_api?key=%s" % (args.domain, invite_key))
	assert r.status_code == 201
	return "xmpp:%s?register;preauth=%s" % (args.domain, r.headers["location"].split("?")[1])

class Client:
	def __init__(self, driver_url, caps, default_id_prefix=""):
		self.caps = caps
		self.driver = webdriver.Remote(driver_url, caps)
		self.id_prefix = default_id_prefix

	def __del__(self):
		self.quit()

	def wait(self, seconds):
		return wait(self.driver, seconds)

	def wait_for(self, el_id, timeout=10):
		if not ':id/' in el_id:
			el_id = self.id_prefix + el_id
		return self.wait(timeout).until(lambda x: x.find_element_by_id(el_id))

	def type(self, el_id, text):
		self.wait_for(el_id)
		el = self.driver.find_element_by_id(el_id if ':id/' in el_id else (self.id_prefix+el_id))
		el.send_keys(text)

	def tap(self, el_id):
		self.wait_for(el_id)
		el = self.driver.find_element_by_id(el_id if ':id/' in el_id else (self.id_prefix+el_id))
		el.click()

	def nav_back(self):
		self.wait(10).until(lambda x: x.find_element_by_accessibility_id('Navigate up'))
		el = self.driver.find_element_by_accessibility_id('Navigate up')
		el.click()

	def back_button(self):
		self.driver.press_keycode(4)

	def quit(self):
		if self.driver:
			self.driver.quit()
			self.driver = None


class SnikketClient(Client):
	def __init__(self, driver_url, caps):
		caps["appWaitActivity"] = "eu.siacs.conversations.ui.WelcomeActivity"
		self.android_version = tuple(map(int, caps["os_version"].split(".")))
		return Client.__init__(self, driver_url, caps, "org.snikket.android:id/")

	def start(self, invite_uri):
		self.driver.start_activity("org.snikket.android", "eu.siacs.conversations.ui.UriHandlerActivity",
			app_wait_package="org.snikket.android", app_wait_activity="eu.siacs.conversations.ui.MagicCreateActivity",
			intent_action="android.intent.action.VIEW " + invite_uri.replace(";", "%3B")
		)

		# MagicCreateActivity - enter username to proceed

		self.type("username", "auto-"+randomword(8))
		self.tap("create_account")

		# Account registration - username and password pre-filled

		self.wait_for("save_button")
		self.tap("save_button")

		# Connecting to server...

		self.wait_for("publish_button", timeout=20)

		# "Publish avatar"

		self.tap("cancel_button")

		# Allow access to contacts
		if self.android_version >= (10, 0):
			self.tap("com.android.permissioncontroller:id/permission_allow_button")
		else:
			self.tap("com.android.packageinstaller:id/permission_allow_button")

		self.wait_for("speed_dial")

def report_status(session_id, success, reason):
	if "browserstack.user" in caps:
		r = requests.put("https://%s:%s@api-cloud.browserstack.com/app-automate/sessions/%s.json" % (
			caps["browserstack.user"], caps["browserstack.key"],
			session_id
		), json={
			"status": "passed" if success else "failed",
			"reason": reason
		})
		if r.status_code != 201 and r.status_code != 200:
			print("Error: Failed to post test result status (received code %d)" % (r.status_code))
			print("Result:", r.text)

def main():
	success = True
	reason = "OK"
	try:
		print("Init...")
		snikket1 = SnikketClient(base_url, caps)

		print("Starting...")
		snikket1.start(get_invite_uri())
	except Exception as e:
		success = False
		reason = "Test threw %s exception. %s" % (type(e).__name__, str(e))
		print(reason)
	finally:
		report_status(snikket1.driver.session_id, success, reason)
		print("Finishing...")
		snikket1.quit()

main()
