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
	
	def send(self, *msg):
		"""Send a raw message to the server."""

		if not self.sock:
			logging.error("Not connected to server")
			return

		message = " ".join(map(str, msg[:-1])) + " :" + str(msg[-1])
		self.sock.sendall(bytes(message + "\r\n", "utf-8"))
		logging.debug("(%s) %s", threading.current_thread().name, message.rstrip())
	
	def say(self, to, msg):
		"""Send a message to a user/channel."""
		self.send("PRIVMSG", to, msg)
	
	def notice(self, to, msg):
		"""Send a notice to a user/channel."""
		self.send("NOTICE", to, msg)
	
	def ctcp_say(self, to, text):
		"""Send a CTCP PRIVMSG message."""
		self.say(to, "\x01{0}\x01".format(text))
	
	def ctcp_notice(self, to, text):
		"""Send a CTCP NOTICE message."""
		self.notice(to, "\x01{0}\x01".format(text))
	
	def action(self, to, msg):
		self.ctcp_say(to, "ACTION {0}".format(msg))
	
	def join(self, chan):
		"""Join a channel."""
		self.send("JOIN", chan)
	
	def part(self, chan, reason=None):
		self.send("PART", chan, reason or "")
	
