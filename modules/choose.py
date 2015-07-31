import random

class ChooseModule:
	def __init__(self, circa):
		self.circa = circa
		self.events = {
			"cmd.roll": [self.roll],
			"cmd.choose": [self.choose]
		}
		self.docs = {
			"choose": "choose <option>, <option>, ... → choose a random <option>",
			"roll": "roll [[a]d[b]] → roll 'a' 'b'-sided dice (default 1d6)"
		}

	def roll(self, fr, to, msg, m):
		a, b = 1, 6
		msg = msg.strip().split(" ", 1)
		if msg:
			l, r = msg[0].split("d")
			try:
				a = int(l)
			except ValueError:
				pass
			try:
				b = int(r)
			except ValueError:
				pass
		values = [str(random.randint(1, b)) for i in range(a)]
		self.circa.say(to, fr + ": " + ", ".join(values))

	def choose(self, fr, to, msg, m):
		opts = [opt.strip() for opt in msg.split(",")]
		if len(opts) <= 1:
			return
		self.circa.say(to, fr + ": " + random.choice(opts))

module = ChooseModule
