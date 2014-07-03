class SlapModule:
	require = "cmd"

	def __init__(self, circa):
		self.circa = circa

		self.listeners = {
			"cmd.slap": [self.slap]
		}

	def slap(self, fr, to, params):
		if to[0] in self.circa.server.types:
			if len(params):
				self.circa.action(to, "slaps {0} around a bit with a large trout".format(params[0]))

module = SlapModule
