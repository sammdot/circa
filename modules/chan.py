class ChannelModule:
	def __init__(self, circa):
		self.circa = circa

	def onload(self):
		self.circa.add_listener("cmd.join", self.circa.join)
		self.circa.add_listener("cmd.leave", self.leave)
		self.circa.add_listener("cmd.goaway", self.leave)
		self.circa.add_listener("cmd.quit", self.quit)

	def onunload(self):
		self.circa.remove_listener("cmd.join", self.circa.join)
		self.circa.remove_listener("cmd.leave", self.leave)
		self.circa.remove_listener("cmd.goaway", self.leave)
		self.circa.remove_listener("cmd.quit", self.quit)

	def leave(self, fr, to, text):
		if self.circa.is_admin(fr) and fr != to:
			self.circa.part(to)

	def quit(self, fr, to, text):
		if self.circa.is_admin(fr):
			self.circa.close()

module = ChannelModule
