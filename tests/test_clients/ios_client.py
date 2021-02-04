from .generic_client import GenericClient
import math

class IOSClient(GenericClient):
	def get_ios_version(self):
		return math.floor(float(self.caps["platformVersion"]))

	def get_device_type(self):
		return "iPad" if self.caps["deviceName"].startswith("iPad ") else "iPhone"
