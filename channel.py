from util import nickcmp, nicklower

class NickDict(dict):
	def __setitem__(self, nick, value):
		dict.__setitem__(self, nicklower(nick), value)

	def __getitem__(self, nick):
		return dict.__getitem__(self, nicklower(nick))

	def __contains__(self, nick):
		return dict.__contains__(self, nicklower(nick))

class Channel:
	def __init__(self, name):
		self.name = name
		self.users = NickDict()
		self.topic = None
		self.mode = set()

	def __contains__(self, nick):
		return nicklower(nick) in self.users
