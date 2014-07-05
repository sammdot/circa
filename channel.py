from util import nickcmp, nicklower

class Channel:
	def __init__(self, name):
		self.name = name
		self.users = {}

	def __contains__(self, nick):
		return nicklower(nick) in self.users.keys()
