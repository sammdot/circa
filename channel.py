from util.nick import nickeq, nicklower

class User:
	def __init__(self, nick, mode=None):
		self.nick = nicklower(nick)
		self.mode = set(mode) if mode else set()
		self.messages = []

	def __repr__(self):
		return "User('{0}')".format(self.nick)

class NickDict(dict):
	def __setitem__(self, nick, value):
		dict.__setitem__(self, nicklower(nick), value)

	def __getitem__(self, nick):
		return dict.__getitem__(self, nicklower(nick))

	def __contains__(self, nick):
		return dict.__contains__(self, nicklower(nick))

	def pop(self, nick):
		return dict.pop(self, nicklower(nick))

	def __getattr__(self, attr):
		if attr in self:
			return self[attr]
		else:
			raise KeyError(attr)

	def __setattr__(self, attr, val):
		self[attr] = val

class Channel:
	def __init__(self, name):
		self.name = name
		self.users = NickDict()
		self.topic = None
		self.mode = set()

	def __repr__(self):
		return "Channel('{1}')".format(self.name)

	def __contains__(self, nick):
		return nick in self.users

class ChannelList(dict):
	def __setitem__(self, chan, val):
		dict.__setitem__(self, chan.lower(), val)

	def __getitem__(self, chan):
		return dict.__getitem__(self, chan.lower())

	def __contains__(self, chan):
		return dict.__contains__(self, chan.lower())

	def __getattr__(self, attr):
		if attr in self:
			return self[attr]
		else:
			raise KeyError(attr)

	def __setattr__(self, attr, val):
		self[attr] = val

