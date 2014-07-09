class LeaveModule:
	require = "cmd"

	def __init__(self, circa):
		self.circa = circa

		self.listeners = {
			"cmd.leave": [self.leave]
		}

	def leave(self, fr, to, params):
		if to[0] in self.circa.server.types:
			chan = self.circa.channels[to]
			if (chan.users[fr] in self.circa.server.prefix_mode and \
				self.circa.server.prefix_mode[chan.users[fr]] in "qaoh") \
				or fr == "sammi":
				self.circa.part(to, "Bye")

module = LeaveModule
