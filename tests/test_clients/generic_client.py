from appium import webdriver
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.common.by import By
import logging

class GenericClient():
	def __init__(self, provider, caps, name=None, logger=None):
		self.provider = provider
		self.caps = caps
		self.logger = logger or logging.getLogger(name or type(self).__name__)
		self.logger.debug("Initializing new client")
		self.driver = webdriver.Remote(provider.url(), provider.caps(caps))
		self.logger.debug("Session initialized")

	def __del__(self):
		self.quit()

	def wait(self, seconds):
		if seconds > 30:
			poll_frequency = 3
		else:
			poll_frequency = 1
		return wait(self.driver, seconds, poll_frequency=poll_frequency)

	def wait_for(self, el_descriptor, by=By.ID, timeout=10):
		return self.wait(timeout).until(lambda x: x.find_element(by, el_descriptor))

	def type(self, el_id, text):
		self.wait_for(el_id)
		el = self.driver.find_element_by_id(el_id)
		el.send_keys(text)

	def tap(self, el_id):
		self.wait_for(el_id)
		el = self.driver.find_element_by_id(el_id)
		el.click()

	def get_view_source(self):
		return self.driver.page_source

	def report_result(self, success, reason=None):
		return self.provider.report(self.driver.session_id, success, reason)

	def save_screenshot(self, filename):
		self.driver.get_screenshot_as_file(filename)
		self.logger.debug("Saved screenshot: " + filename)

	def quit(self):
		if hasattr(self, 'driver') and self.driver != None:
			self.logger.debug("Quitting")
			self.driver.quit()
			self.driver = None
