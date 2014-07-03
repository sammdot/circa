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
			"cmd.trivia": [self.start],
			"cmd.endtrivia": [self.end],
		}

	def start(self, fr, to, params):
		if len(params) == 0:
			return
		host = params[0]
		if to in self.games:
			self.circa.say(to, "trivia already running in {0}".format(to))
		elif to in self.circa.channels:
			if host in self.circa.channels[to].users:
				self.games[to] = game = Trivia(self.circa, to, host)
				self.circa.say(to, "started trivia in {0} - your host is {1}".format(to, host))
			else:
				self.circa.say(to, "no user {0} in {1}".format(host, to))
		else:
			self.circa.say(to, "cannot start trivia here")

	def end(self, fr, to, params):
		if to in self.games:
			game = self.games[to].host
			...
		else:
			self.circa.say("no trivia running in {0}".format(to))

module = TriviaModule
