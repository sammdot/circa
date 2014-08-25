from util.esc import unescape

class SayModule:
	require = "cmd"

	def __init__(self, circa):
		self.circa = circa
		self.events = {
			"cmd.say": [self.say]
		}

	def say(self, fr, to, msg, m):
		if self.circa.is_admin(m.prefix):
			self.circa.say(to, unescape(msg))

module = SayModule
