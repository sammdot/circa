class Trivia:
	def __init__(self, circa, channel, host):
		self.circa = circa
		self.users = list(circa.channels[channel].users.keys())
		self.scores = {user: 0 for user in self.users}

		self.host = host

class TriviaModule:
	def __init__(self, circa):
		self.circa = circa
		self.games = {}

		self.listeners = {
			"cmd.trivia": [self.start]
		}

	def start(self, fr, to, params):
		if to in self.circa.channels and len(params):
			host = params[0]
			self.games[to] = game = Trivia(self.circa, to, host)

module = TriviaModule
