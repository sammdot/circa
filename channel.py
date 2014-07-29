from util.nick import nickeq, nicklower

class User:
	def __init__(self, nick, mode=None, registered=False):
		self.nick = nicklower(nick)
		self.registered = registered
		self.mode = set(mode) if mode else set()

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
		return self[attr] if attr in self else dict.__getattr__(self, attr)

	def __setattr__(self, attr, val):
		if attr in self:
			self[attr] = val
		else:
			dict.__setattr__(self, attr, val)

class Channel:
	def __init__(self, name):
		self.name = name
		self.users = NickDict()
		self.topic = None
		self.mode = set()
	
	def __repr__(self):
		return "Channel({0})".format(self.name)
	
	def __contains__(self, nick):
		return nick in self.users

class ChannelList(dict):
	def __getattr__(self, attr):
		return self[attr] if attr in self else None

	def __setattr__(self, attr, val):
		if attr in self:
			self[attr] = val

