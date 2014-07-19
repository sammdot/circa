import logging
import re
import socket
import threading

from channel import Channel, ChannelList
from message import Message
from server  import Server

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
		self.listeners = {}

		self.nickmod = 0

		if self.conf["autoconn"]:
			threading.Thread(target=self.connect).start()
	
	def connect(self):
		"""Attempt to connect to the server. Log in if successful."""

		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		try:
			self.sock.connect((self.conf["server"], self.conf["port"]))
			self.server = Server(self.conf["server"], self.conf["port"])
			logging.info("Connected to %s", self.server.host)

			threading.Thread(name="listen", target=lambda: None).start()
		except socket.error as e:
			logging.error("Cannot connect to %s: %s", self.conf["server"], e)
			self.sock.close()
			self.sock = None
