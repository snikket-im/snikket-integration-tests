#!/usr/bin/env python3

import logging
import sys
import time
import traceback

from test_clients import SnikketAndroidClient, SnikketIOSClient
from providers import BrowserStack, SauceLabs
from util import *
from concurrent.futures.thread import ThreadPoolExecutor
import concurrent.futures

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
parser.add_argument("--caps-file", help="Add caps from JSON file", action='append', dest='caps_files')
parser.add_argument("--cap", help="Specify a single capability entry (e.g. foo=bar)", action='append', dest='caps'),
parser.add_argument("--browserstack-config", help="Specify path to BrowserStack configuration")
parser.add_argument("--saucelabs-config", help="Specify path to SauceLabs configuration")
args = parser.parse_args()

logging.basicConfig(format='%(asctime)s %(name)s %(message)s', datefmt="%H:%M:%S")

global_caps = {}

if args.caps_files:
	for caps_filename in args.caps_files:
		global_caps.update(get_caps_from_file(caps_filename))

if args.caps:
	for cap_entry in args.caps:
		s = cap_entry.split("=", 2)
		global_caps[s[0]] = s[1]

if args.saucelabs_config:
	saucelabs = SauceLabs(get_caps_from_file(args.saucelabs_config))

if args.browserstack_config:
	browserstack = BrowserStack(get_caps_from_file(args.browserstack_config))


def run_ios_tests(client, params):
	client.logger.info("Running iOS tests...")
	# Appium doesn't like xmpp: URIs, and there doesn't appear
	# to be a way to feed it directly to the app on iOS (unlike
	# Android intents), so for now we have to manually register
	# the account :(
	account = get_new_account(params["username"], params["domain"], params["invite_key"])

	contact_jid = params["contact_username"] + "@" + params["domain"]

	client.start()
	client.sign_in(account.jid, account.password)

	# Open 'Settings'
	client.tap("Settings")
	# Open 'Chats' settings page
	client.tap("settingsViewCell")
	# Switch to OMEMO encryption
	client.tap("MessageEncryptionTableViewCell")
	client.tap("OMEMO")
	client.tap("Back")
	# Leave 'Chats' settings page
	#client.driver.find_element_by_xpath("//*/XCUIElementTypeNavigationBar/XCUIElementTypeButton[@name='Settings']").click()
	client.navbar_button("Settings")
	# Leave 'Settings' area (back to main screen)
	client.tap("Close")

	# Show 'Contacts' screen
	client.show_contacts()
	# Search for our contact
	client.type("Search", params["contact_username"])
	client.wait_for_contact(contact_jid)
	client.send_message("Hello, friend! I am using Snikket on iOS.")
	client.send_message("This is another message from iOS, how are you? \U0001F600")
	# Weird way to find the 'Back' button
	# TODO: Needs an id
	client.driver.find_element_by_xpath("//*/XCUIElementTypeNavigationBar/XCUIElementTypeButton[@name='Contacts']").click()
	# Leave contact search mode
	client.tap("Cancel")
	# Switch to chats list
	client.show_chats()
	client.join_group_chat("general@groups."+params["domain"], "General Chat")
	client.send_message("Hello, group! I'm using Snikket on iOS.")
	# Weird way to find the 'Back' button
	# TODO: Needs an id
	client.driver.find_element_by_xpath("//*/XCUIElementTypeNavigationBar/XCUIElementTypeButton[@name='Chats']").click()

	client.create_private_group(params["private_group_name"], contacts = [contact_jid])
	time.sleep(3)
	client.send_message("Hi! Welcome to the private group!")
	time.sleep(3)


def run_android_tests(client, params):
	client.logger.info("Running Android tests...")
	invite_uri = get_new_invite_uri(params["domain"], params["invite_key"])
	client.start(invite_uri, params["username"])
	# Exit "Start Conversation..." screen
	client.back_button()

	# Open general group chat
	client.open_group_chat("general@groups."+params["domain"], public=True)
	client.send_message("Hello, group! I am using Snikket on Android \U0001F60E")
	client.back_button()

	# Wait for incoming message from iOS client
	client.wait_for_message(params["contact_username"])
	client.send_message("Hello! I am using Snikket on Android.")
	client.send_message("\U0001F600")
	client.open_contact_details()
	# Back to main screen
	client.back_button()
	client.back_button()

	client.open_settings()
	# Fragile, assumes 3 pages long. Could detect 'About' as the last entry?
	for i in range(3):
		# Switches to keyboard navigation
		client.page_down()
		# Actually scroll down a page
		client.page_down()
		# Hide the keyboard focus highlight by tapping the toolbar
		# (which is otherwise a noop)
		client.tap("toolbar")
	client.back_button()

	# Wait for iOS client to add us to a private group
	client.wait_for_new_chat_and_open(params["private_group_name"])
	client.send_message("Ah, this is a private group. Ssshh!")
	# Approve OMEMO keys
	client.tap("save_button")
	# Return to main chats screen
	client.back_button()

	client.open_manage_accounts()
	client.open_account()
	client.account_set_name("Snikket Android User")
	client.account_show_server_info()
	client.back_button()
	client.back_button()
	time.sleep(60)

def ios_thread(params):
	success = True
	reason = "OK"

	logger = logging.getLogger("iOS")
	logger.setLevel("DEBUG")

	ios_client = None

	try:
		ios_client_caps = dict(global_caps)
		ios_client_caps.update(get_caps_from_file("devices/ios/iOS 13 on iPhone 11.json"))
		ios_client = SnikketIOSClient(saucelabs, ios_client_caps, logger = logger)
		run_ios_tests(ios_client, params)
	except Exception as e:
		success = False
		reason = "Test (iOS) threw %s exception. %s" % (type(e).__name__, str(e))
		logger.error(reason)
		logger.error(traceback.format_exc())
	finally:
		if ios_client:
			logger.debug("Final iOS view:\n"+ios_client.get_view_source())
			ios_client.report_result(success, reason)
			ios_client.quit()
	return success

def android_thread(params):
	success = True
	reason = "OK"

	logger = logging.getLogger("Android")
	logger.setLevel("DEBUG")

	logger.debug("Waiting 30s because iOS test is slower")
	time.sleep(30)

	android_client = None

	try:
		android_client_caps = dict(global_caps)
		android_client_caps.update(get_caps_from_file("devices/android/Android 10 on Pixel 3.json"))
		android_client = SnikketAndroidClient(browserstack, android_client_caps, logger = logger)
		run_android_tests(android_client, params)

	except Exception as e:
		success = False
		reason = "Test (Android) threw %s exception. %s" % (type(e).__name__, str(e))
		logger.error(reason)
		logger.error(traceback.format_exc())
	finally:
		if android_client:
			logger.debug("Final Android view:\n"+android_client.get_view_source())
			android_client.report_result(success, reason)
			android_client.quit()
	return success

def main():
	success = True
	reason = "OK"
	logger = logging.getLogger(__name__)
	logger.setLevel("DEBUG")

	logger.info("Starting...")

	with ThreadPoolExecutor(max_workers=2) as executor:
		android_username = generate_random_username("auto-android-")
		ios_username = generate_random_username("auto-ios-")
		private_group_name = generate_random_username("Test group ")
		ios_result = executor.submit(ios_thread, {
			"domain": args.domain,
			"invite_key": args.invite_key,
			"username": ios_username,
			"contact_username": android_username,
			"private_group_name": private_group_name
		})
		android_result = executor.submit(android_thread, {
			"domain": args.domain,
			"invite_key": args.invite_key,
			"username": android_username,
			"contact_username": ios_username,
			"private_group_name": private_group_name
		})

		for result in concurrent.futures.as_completed([ios_result, android_result], timeout=1800):
			if result.result() != True:
				success = False

	logger.info("Worker threads finished")

	if success:
		logger.info("ALL TESTS PASSED")
	else:
		logger.error("TESTS HAVE FAILED")

	return 0 if success else 1


sys.exit(main())
