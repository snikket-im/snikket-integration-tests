#!/usr/bin/env python3

import sys

from test_clients import SnikketAndroidClient

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

def add_caps_from_file(current_caps, caps_filename):
	with open(caps_filename, 'r') as caps_file:
		new_caps = json.loads(caps_file.read())
		for cap_name in new_caps:
			current_caps[cap_name] = new_caps[cap_name]


if args.caps_files:
	for caps_filename in args.caps_files:
		add_caps_from_file(caps, caps_filename)

if args.caps:
	for cap_entry in args.caps:
		s = cap_entry.split("=", 2)
		caps[s[0]] = s[1]

def randomword(length):
	letters = string.ascii_lowercase
	return ''.join(random.choice(letters) for i in range(length))

def get_invite_uri():
	print("Creating invite...")
	r = requests.get("https://%s/invites_api?key=%s" % (args.domain, invite_key))
	assert r.status_code == 201
	print("Invite created")
	return "xmpp:%s?register;preauth=%s" % (args.domain, r.headers["location"].split("?")[1])


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
		snikket1 = SnikketAndroidClient(base_url, caps)

		print("Starting...")
		snikket1.start(get_invite_uri(), "auto-"+randomword(8))
	except Exception as e:
		success = False
		reason = "Test threw %s exception. %s" % (type(e).__name__, str(e))
		print(reason)
	finally:
		report_status(snikket1.driver.session_id, success, reason)
		print("Finishing...")
		snikket1.quit()
		return 0 if success else 1

sys.exit(main())
