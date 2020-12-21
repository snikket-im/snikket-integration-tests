from .android_client import AndroidClient

class SnikketAndroidClient(AndroidClient):
	def __init__(self, driver_url, caps):
		caps["appWaitActivity"] = "eu.siacs.conversations.ui.WelcomeActivity"
		self.android_version = tuple(map(int, caps["os_version"].split(".")))
		return AndroidClient.__init__(self, driver_url, caps, "org.snikket.android:id/")

	def start(self, invite_uri, username):
		self.driver.start_activity("org.snikket.android", "eu.siacs.conversations.ui.UriHandlerActivity",
			app_wait_package="org.snikket.android", app_wait_activity="eu.siacs.conversations.ui.MagicCreateActivity",
			intent_action="android.intent.action.VIEW " + invite_uri.replace(";", "%3B")
		)

		# MagicCreateActivity - enter username to proceed

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

		self.wait_for("speed_dial")
