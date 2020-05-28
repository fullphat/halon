from colour import Color

class DeviceInfo(object):

	def __init__(self):
		self.on = False
		self.colour = Color("black")
		self.thread = None

	def IsOn(self):
		return self.on

	def SetIsOn(self, isOn):
		self.on = isOn

	def Colour(self):
		return self.colour

	def Thread(self):
		return self.thread


