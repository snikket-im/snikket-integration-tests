from .android_client import AndroidClient
from selenium.webdriver.support import expected_conditions as expect
from selenium.webdriver.common.by import By

def conversation_with_name(name):
	def matcher(driver):
		conversations = driver.find_elements_by_id("org.snikket.android:id/conversation_name")
		for conversation in conversations:
			if conversation.text and conversation.text == name:
				return conversation
		return False
	return matcher

class SnikketAndroidClient(AndroidClient):
	def __init__(self, provider, caps, logger=None):
		caps["appWaitActivity"] = "eu.siacs.conversations.ui.WelcomeActivity"
		self.android_version = tuple(map(int, caps["os_version"].split(".")))
		return AndroidClient.__init__(self, provider, caps, "org.snikket.android:id/", logger=logger)

	def start(self, invite_uri, username):
		self.driver.start_activity("org.snikket.android", "eu.siacs.conversations.ui.UriHandlerActivity",
			app_wait_package="org.snikket.android", app_wait_activity="eu.siacs.conversations.ui.MagicCreateActivity",
			intent_action="android.intent.action.VIEW " + invite_uri.replace(";", "%3B")
		)

		# MagicCreateActivity - enter username to proceed

		self.logger.debug("Registering account %s", username)

		self.type("username", username);
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

		self.logger.debug("Waiting for main screen...")
		self.wait_for("speed_dial")
		self.logger.debug("Main screen reached!")
		self.dismiss_notification()

		self.logger.debug("Leaving 'Start Conversation...' screen...")
		# Exit "Start Conversation..." screen
		self.back_button()
		self.logger.debug("Done")

		try:
			self.logger.debug("Dismissing battery optimization warning...")
			# Wait for battery optimizations warning
			self.wait_for("alertTitle")
			# Dismiss
			self.back_button()
			self.logger.debug("Dismissed.")
		except:
			self.logger.debug("Not found. Continuing...")

	def dismiss_notification(self):
		self.logger.debug("Swiping away notification")
		self.driver.swipe(50, 100, 500, 100)
		self.logger.debug("Swiped")

	def open_bookmarks(self):
		self.logger.debug("Opening bookmarks")
		self.tap("fab")
		self.driver.find_elements_by_class_name("android.support.v7.app.ActionBar$Tab")[1].click()

	def open_group_chat(self, jid, public=False):
		self.logger.debug("Opening group chat "+jid)
		self.open_bookmarks()
		self.tap("action_search")
		self.type("search_field", jid)
		self.tap("contact_display_name")
		self.logger.debug("Opened "+jid)
		if public:
			self.logger.debug("Accepting warning about public JID...")
			self.tap("snackbar_action")
			self.logger.debug("Accepted")

	def wait_for_message(self, contact_username):
		self.logger.debug("Waiting for message from %s", contact_username)
		self.wait(160).until(expect.text_to_be_present_in_element((By.ID, "org.snikket.android:id/conversation_name"), contact_username))
		self.logger.debug("Message received! Opening...")
		self.tap("org.snikket.android:id/conversation_name")

	def send_message(self, text):
		self.type("textinput", text)
		self.tap("textSendButton")

	# From conversation view, open contact details
	def open_contact_details(self):
		self.logger.debug("Opening contact details...")
		self.menu_button()
		# Fragile, assumes 'Contact details' is always first menu entry
		self.driver.find_elements(By.ID, "org.snikket.android:id/title")[0].click()

	# From main screen, open settings
	def open_settings(self):
		self.logger.debug("Opening settings...")
		self.menu_button()
		# Fragile, assumes 'Settings' is 4th menu entry
		self.driver.find_elements(By.ID, "org.snikket.android:id/title")[2].click()

	def account_set_name(self, name):
		self.logger.debug("Setting my display name...")
		self.tap("action_edit_your_name")
		self.type("input_edit_text", name)
		self.tap("android:id/button1")
		self.logger.debug("Set!")

	def account_show_server_info(self):
		self.logger.debug("Enabling 'Show server info' checkbox")
		# Open menu
		self.menu_button()
		# Fragile!
		self.tap("checkbox")

	# From main screen, open 'Manage accounts'
	def open_manage_accounts(self):
		self.logger.debug("Opening 'Manage accounts'...")

		self.menu_button()
		# Fragile, assumes 'Manage accounts' is 3rd menu entry
		self.driver.find_elements(By.ID, "org.snikket.android:id/title")[2].click()

	# From 'Manage accounts' open first account
	def open_account(self):
		self.logger.debug("Selecting first account...")
		self.tap("account_jid")

	def wait_for_new_chat_and_open(self, name, timeout=180):
		self.logger.debug("Waiting for chat '%s'...", name)
		conversation = self.wait(timeout).until(conversation_with_name(name))
		self.logger.debug("Chat found! Opening...")
		conversation.click()
		self.logger.debug("Chat opened")
