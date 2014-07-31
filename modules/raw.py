class RawModule:
	require = "cmd"

	def __init__(self, circa):
		self.circa = circa
		self.events = {
			"cmd.raw": [self.raw]
		}

	def raw(self, fr, to, msg, m):
		if self.circa.is_admin(m.prefix):
			self.circa.send(msg)

module = RawModule
