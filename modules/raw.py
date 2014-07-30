class RawModule:
	def __init__(self, circa):
		self.circa = circa

	def onload(self):
		self.circa.add_listener("cmd.raw", self.raw)

	def onunload(self):
		self.circa.remove_listener("cmd.raw", self.raw)

	def raw(self, fr, to, msg):
		if self.circa.is_admin(fr):
			self.circa.send(msg)

module = RawModule
