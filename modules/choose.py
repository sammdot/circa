import random

class ChooseModule:
	def __init__(self, circa):
		self.circa = circa
		self.events = {
			"cmd.roll": [self.roll],
			"message": [self.dotchoose],
			"cmd.choose": [self.choose]
		}

	def roll(self, fr, to, msg, m):
		a, b = 1, 6
		msg = msg.strip().split(" ", 1)
		if msg:
			l, r = msg[0].split("d")
			try:
				a = int(l)
				b = int(r)
			except ValueError:
				pass
		values = [str(random.randint(1, b)) for i in range(a)]
		self.circa.say(to, fr + ": " + ", ".join(values))

	def choose(self, fr, to, msg, m):
		opts = [opt.strip() for opt in msg.split(",")]
		self.circa.say(to, fr + ": " + random.choice(opts))

	def dotchoose(self, fr, to, msg, m):
		target = fr if to == self.circa.nick else to
		cmd, opts = msg.split(" ", 1)
		if cmd == ".choose":
			self.choose(fr, target, opts, m)

module = ChooseModule
