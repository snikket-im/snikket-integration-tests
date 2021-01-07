from .ios_client import IOSClient
from selenium.webdriver.common.by import By

class SnikketIOSClient(IOSClient):
	def start(self):
		self.logger.debug("Start...")
		# Grant push notifications permission
		self.tap("Allow")

	# From the welcome screen, sign in using
	# the provided credentials
	def sign_in(self, jid, password):
		self.logger.debug("Sign in")
		self.tap("Sign in")

		# Input JID and password
		# TODO: These elements could do with a name
		self.driver.find_element_by_class_name("XCUIElementTypeTextField").send_keys(jid)
		self.driver.find_element_by_class_name("XCUIElementTypeSecureTextField").send_keys(password)

		# Submit
		self.tap("Save")

		# Wait for main screen to appear, indicating success
		self.logger.debug("Waiting for main screen...")
		self.wait_for("Chats", timeout=60)
		self.wait_for("Contacts", timeout=60)
		self.logger.debug("Reached main screen!")

	# From the main screen, switch to Contacts view
	def show_contacts(self):
		self.tap("Contacts")

	def show_chats(self):
		self.tap("Chats")

	def wait_for_contact(self, contact_jid):
		self.logger.debug("Waiting for %s", contact_jid)
		self.wait_for(contact_jid, timeout=60)
		self.tap(contact_jid)

	# Inside a conversation, sends and types a message
	def send_message(self, text):
		self.logger.debug("Sending message: %s", text)
		self.driver.find_element_by_class_name("XCUIElementTypeTextView").send_keys(text)
		self.tap("paperplane.fill")

	def wait_for_message(self, username):
		self.logger.debug("Waiting for message from %s", username)
		self.wait_for("new_message")

	def join_group_chat(self, jid, name):
		self.logger.debug("Joining group chat: %s", jid)
		self.tap("Add")
		self.tap("Join group chat")
		self.tap(jid)
		self.tap("Next")
		self.tap("Join")
		self.tap(name)

	# From the main Chats screen, create a private group
	def create_private_group(self, name, contacts=[]):
		self.logger.debug("Creating private group (%s)...", name)
		self.tap("Add")
		self.tap("New private group chat")
		# Enter name
		self.driver.find_element_by_class_name("XCUIElementTypeTextField").send_keys(name)
		# Tap 'Next'
		self.tap("Next")
		# Tap 'Create'
		self.tap("Create")
		# We are at the Chats screen

		# Open group (by name)
		self.tap(name)

		self.logger.debug("Group created!")

		# Tap members icon (??)
		self.navbar_button(index=1)

		# For each contact:
		for contact in contacts:
			self.logger.debug("Adding contact to group (%s)", contact)
			# Tap add icon
			self.tap("Add")
			# Tap search input and enter contact JID
			self.type("Search", contact)
			# Tap contact JID in results to add them
			self.tap(contact)
			# We are at the members screen again
			self.logger.debug("Contact added. Awaiting visual confirmation...")
			self.wait_for(contact.split("@")[0])

		# Tap group name in navbar to go back
		self.navbar_button(name)

	def navbar_button(self, name=None, index=0):
		xpath = "//*/XCUIElementTypeNavigationBar/XCUIElementTypeButton"
		if name:
			xpath = xpath + "[@name='" + name + "']"
		self.logger.debug("Tapping navbar button %s[%d]", xpath, index)
		self.driver.find_elements_by_xpath(xpath)[index].click()
		self.logger.debug("Tapped navbar button")
