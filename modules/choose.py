import random

class ChooseModule:
	def __init__(self, circa):
		self.circa = circa
		self.events = {
			"message": [self.dotchoose],
			"cmd.choose": [self.choose]
		}

	def choose(self, fr, to, msg, m):
		opts = [opt.strip() for opt in msg.split(",")]
		self.circa.say(to, fr + ": " + random.choice(opts))

	def dotchoose(self, fr, to, msg, m):
		target = fr if to == self.circa.nick else to
		cmd, opts = msg.split(" ", 1)
		if cmd == ".choose":
			self.choose(fr, target, opts, m)

module = ChooseModule
