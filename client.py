import socket
import threading

from channel import Channel, ChannelList

class Client:
	def __init__(self, server, nick, username, realname, **conf):
		self.sock = None
		self.nick = None
		self.server = None

		self.conf = {
			"port": 6667,
			"autorejoin": True,
			"autoconn": True,
			"channels": [],
			"prefixes": "&#"
		}

		self.conf.update(conf)
		self.conf.update({
			"server": server,
			"nick": nick,
			"username": username,
			"realname": realname,
		})

		self.channels = ChannelList()
