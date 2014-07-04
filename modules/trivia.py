class Trivia:
	def __init__(self, circa, channel, host):
		self.circa = circa
		self.users = list(circa.channels[channel].users.keys())
		self.users.remove(self.circa.nick)
		self.users.remove(host)
		self.scores = {user: 0 for user in self.users}

		self.host = host

		self.questions = []
		self.answers = []
		self.listening = False
		self.queue = []

		self.curuser = None
		self.curans = None

	def ask(self, question):
		self.questions.append(question)
		self.listening = True

	def answer(self):
		self.scores[self.curuser] += 1
		self.answers.append((self.curuser, self.curans))
		self.curuser = None
		self.curans = None
		self.queue = []
		self.listening = False

	def wrong(self):
		self.scores[self.curuser] -= 1
		self.queue.pop(0)
		self.curuser = self.queue[0]

	def next(self):
		self.queue.pop(0)
		self.curuser = self.queue[0]

class TriviaModule:
	def __init__(self, circa):
		self.circa = circa
		self.games = {}

		self.listeners = {
			"cmd.trivia": [self.start],
			"cmd.endtrivia": [self.end],
			"cmd.q": [self.question],
			"cmd.a": [self.answer],
			"cmd.right": [self.right],
			"cmd.wrong": [self.wrong],
			"message": [self.buzz],
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
			game = self.games[to]
			if fr == game.host:
				sorted_scores = sorted(game.scores.items(), key=lambda i: -i[1])
				final = ["{0} = {1}".format(*x) for x in sorted_scores]
				self.circa.say(to, "game over. final scores: " + ", ".join(final))
				self.circa.say(to, "congratulations \x02{0}\x02!".format(sorted_scores[0][0]))
				self.games.pop(to)
			else:
				self.circa.say(to, "{0}: you are not trivia host".format(fr))
		else:
			self.circa.say(to, "no trivia running in {0}".format(to))

	def question(self, fr, to, params):
		if to in self.games:
			self.games[to].ask(" ".join(params))

	def answer(self, fr, to, params):
		if to in self.games:
			game = self.games[to]
			if fr == game.curuser:
				ans = " ".join(params)
				game.curans = ans
			elif fr == game.host:
				pass
			else:
				self.circa.say(to, "{0}: wait for your turn".format(fr))

	def buzz(self, fr, to, params, msg):
		if to in self.games:
			game = self.games[to]
			if "".join(params).strip().lower() == "x":
				if fr in game.users and fr != game.host:
					game.queue.append(fr)
					if len(game.queue) == 1:
						self.circa.say(to, "\x02{0}\x02".format(game.queue[0]))
						game.curuser = game.queue[0]

	def right(self, fr, to, params):
		if to in self.games:
			game = self.games[to]
			if fr == game.host:
				self.circa.say(to, "{0} +1".format(game.curuser))
				game.answer()

	def wrong(self, fr, to, params):
		if to in self.games:
			game = self.games[to]
			if fr == game.host:
				self.circa.say(to, "{0} -1".format(game.curuser))
				game.wrong()
				self.circa.say(to, "\x02{0}\x02, ".format(game.queue[0]) + ", ".join(game.queue[1:]))

module = TriviaModule
