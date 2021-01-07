from .generic_client import GenericClient

class AndroidClient(GenericClient):
	def __init__(self, provider, caps, default_id_prefix="", logger = None):
		self.id_prefix = default_id_prefix
		return GenericClient.__init__(self, provider, caps, logger = logger)

	def wait_for(self, el_id, timeout=10):
		if not ':id/' in el_id:
			el_id = self.id_prefix + el_id
		return GenericClient.wait_for(self, el_id, timeout=timeout)

	def type(self, el_id, text):
		self.wait_for(el_id)
		el = self.driver.find_element_by_id(el_id if ':id/' in el_id else (self.id_prefix+el_id))
		el.send_keys(text)

	def tap(self, el_id):
		self.wait_for(el_id)
		el = self.driver.find_element_by_id(el_id if ':id/' in el_id else (self.id_prefix+el_id))
		el.click()

	# Android-only methods
	def nav_back(self):
		self.wait(10).until(lambda x: x.find_element_by_accessibility_id('Navigate up'))
		el = self.driver.find_element_by_accessibility_id('Navigate up')
		el.click()

	def back_button(self):
		self.driver.press_keycode(4)

	def menu_button(self):
		self.driver.press_keycode(82)

	def page_up(self):
		self.driver.press_keycode(92)

	def page_down(self):
		self.driver.press_keycode(93)

