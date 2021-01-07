import requests

class BrowserStack():
	def __init__(self, config):
		self.config = config

	def url(self):
		return "https://hub-cloud.browserstack.com/wd/hub"
		return "https://{0}:{1}@hub-cloud.browserstack.com/wd/hub".format(
			self.config["browserstack.user"],
			self.config["browserstack.key"]
		)

	def caps(self, base_caps={}):
		new_caps = base_caps.copy()
		new_caps.update(self.config)
		return new_caps

	def report(self, session_id, success, reason=None):
		report_url = "https://{0}:{1}@api-cloud.browserstack.com/app-automate/sessions/{2}.json".format(
			self.config["browserstack.user"],
			self.config["browserstack.key"],
			session_id
		)
		r = requests.put(report_url, json={
			"status": "passed" if success else "failed",
			"reason": reason
		})
		if r.status_code != 201 and r.status_code != 200:
			print("Error: Failed to post test result status to BrowserStack (received code %d)" % (r.status_code))
			print("Result:", r.text)

class SauceLabs():
	def __init__(self, config):
		self.config = config

	def url(self):
		return "http://{config[saucelabs.user]}:{config[saucelabs.key]}@ondemand.us-west-1.saucelabs.com:80/wd/hub".format(
			config=self.config
		)

	def caps(self, base_caps={}):
		return base_caps

	def report(self, session_id, success, reason=None):
		pass
