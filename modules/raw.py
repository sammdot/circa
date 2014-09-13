from util.esc import unescape

class RawModule:
	require = "cmd"

	def __init__(self, circa):
		self.circa = circa
		self.events = {
			"cmd.raw": [self.raw]
		}
		self.docs = {
			"raw": "raw [msg] → send a raw IRC message. Admins only."
		}

	def raw(self, fr, to, msg, m):
		if self.circa.is_admin(m.prefix):
			self.circa.send(unescape(msg))

module = RawModule
