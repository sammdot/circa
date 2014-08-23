import re

class SedModule:
	subre = re.compile(r"^(?:(\S+)[:,]\s)?(?:s|(.+?)/s)/((?:\\/|[^/])+)\/((?:\\/|[^/])*?)/([gixs]{0,4})?(?: .*)$")

	def __init__(self, circa):
		self.circa = circa
		self.events = {
			"message": [self.sub]
		}

	def sub(self, fr, to, msg, m):
		match = self.subre.match(msg)
		if match:
			self.circa.channels[to[1:]].users[fr].messages.pop()
			target, search, lhs, rhs, flags = match.groups()
			lhsre = re.compile(lhs)
			user = target or fr
			msgs = self.circa.channels[to[1:]].users[user].messages[::-1]
			if search:
				msgs = [line for line in msgs if search in line]
			msgs = [line for line in msgs if lhsre.search(line)]
			if len(msgs):
				t = msgs[0]
				f = 0
				if "i" in flags: f |= re.I
				if "x" in flags: f |= re.X
				if "s" in flags: f |= re.S
				count = int("g" not in flags)
				if t.startswith("\x01ACTION "):
					t = t[len("\x01ACTION "):-1]
					t = lhsre.sub(rhs, t, count=count, flags=f)
					self.circa.say(to, "\x02* {0}\x02 {1}".format(user, t))
				else:
					t = lhsre.sub(rhs, t, count=count, flags=f)
					self.circa.say(to, "<{0}> {1}".format(user, t))

module = SedModule
