import random
import re

class ChooseModule:
	def __init__(self, circa):
		self.circa = circa

		self.listeners = {
			"cmd.choose": [self.choose],
			"cmd.roll": [self.roll],
		}

	def choose(self, fr, to, params):
		params = " ".join(params).strip()
		if len(params) == 0:
			self.circa.notice(fr, "choose <choice>, ... or <choice>")
		else:
			choices = re.split(r"\s*,\s*|\bor\b", " ".join(params))
			self.circa.say(to, "{0}: {1}".format(fr, random.choice(choices)))

	def roll(self, fr, to, params):
		numdice, amtdice = 1, 6
		if len(params):
			dice = params[0]
			if dice.count("d") > 1:
				self.circa.notice(fr, "roll <n>d<n>")
			a, b = 1, 6
			if "d" in dice:
				a, b = dice.split("d")
			try:
				numdice = int(a)
			except ValueError:
				pass
			try:
				amtdice = int(b)
			except ValueError:
				pass
		self.circa.say(to, "{0}: {1}".format(fr, ", ".join(
			[str(random.randrange(1, amtdice)) for i in range(numdice)])))

module = ChooseModule
