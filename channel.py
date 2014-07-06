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

	def __repr__(self):
		return "Channel({0})".format(self.name)

	def __contains__(self, nick):
		return nicklower(nick) in self.users

class ChannelList:
	def __init__(self):
		self._channels = {}

	def __getattr__(self, chan):
		return self._channels[chan] if chan in self._channels else None

	def __setattr__(self, chan, value):
		self._channels[chan] = value

	def __contains__(self, chan):
		return chan in self._channels
