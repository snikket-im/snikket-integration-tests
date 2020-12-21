class AndroidClient:
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
