import logging
import socket
import threading

from channel import Channel, ChannelList
from message import Message

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

		if self.conf["autoconn"]:
			thread = threading.Thread(name=self.conf["server"], target=self.connect)
			logging.debug("server %s", thread.name)
			thread.start()

	def connect(self):
		"""Attempt to connect to the server. Log in if successful."""

		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		try:
			self.sock.connect((self.conf["server"], self.conf["port"]))
			self.server = self.conf["server"]
			logging.info("%s connected", self.server)

			self.send("NICK", self.conf["nick"])
			self.send("USER", self.conf["username"], 8, "*", self.conf["realname"])

			thread = threading.Thread(name=self.conf["server"] + "-listen", target=self.listen)
			logging.debug("listener %s", thread.name)
			thread.start()
		except socket.error as e:
			logging.error("%s cannot connect: %s", self.conf["server"], e)
			self.sock.close()
			self.sock = None

	def send(self, *msg):
		"""Send a raw message to the server. Prepend a colon to the last parameter."""

		if not self.sock:
			logging.error("%s not connected to server", self.conf["server"])
			return

		message = " ".join(map(str, msg[:-1])) + " :" + str(msg[-1])
		self.sock.sendall(bytes(message + "\r\n", "utf-8"))
		logging.debug("Send: %s", message.rstrip())

	def say(self, to, msg):
		"""Send a message to a user or channel."""
		self.send("PRIVMSG", to, msg)

	def notice(self, to, msg):
		"""Send a notice to a user or channel."""
		self.send("NOTICE", to, msg)

	def ctcp(self, to, type, text):
		"""Send a CTCP message. 'type' is either 'privmsg' or 'notice'."""
		(self.say if type == "privmsg" else self.notice)(to, "\x01{0}\x01".format(text))

	def action(self, to, msg):
		self.ctcp(to, "privmsg", "ACTION {0}".format(msg))

	def join(self, chan):
		"""Join a channel."""
		self.send("JOIN", chan)

	def part(self, chan, reason=""):
		"""Leave a channel (and optionally provide a reason)."""
		self.send("PART", chan, reason)

	def listen(self):
		"""Listen for incoming messages from the IRC server."""
		if not self.sock:
			logging.error("%s not connected to server", self.conf["server"])
			return

		buf = ""
		while True:
			buf += str(self.sock.recv(4096), "utf-8")
			*msgs, buf = buf.split("\r\n")
			for msg in msgs:
				m = Message.parse(msg)
				thread = threading.Thread(target=lambda: self.handle(m))
				logging.debug("%s handler thread %s [%s]",
					threading.current_thread().name, thread.name, m.command)
				thread.start()

	def add_listener(self, event, function):
		"""Add a function to listen for the specified event."""
		if event not in self.listeners:
			self.listeners[event] = []
		self.listeners[event].append(function)

	def remove_listener(self, event, function):
		"""Remove a function as a listener from the specified event."""
		if event not in self.listeners:
			return
		self.listeners[event] = [l for l in self.listeners[event] if l != function]

	def remove_listeners(self, event):
		"""Remove all functions listening for the specified event."""
		if event not in self.listeners:
			return
		del self.listeners[event]

	def emit(self, event, *params):
		"""Emit an event, and pass the parameters to all functions listening for the event."""
		if event in self.listeners:
			for listener in self.listeners[event]:
				try:
					thread = threading.Thread(target=lambda: listener(*params))
					logging.debug("%s worker thread %s [%s, %s]",
						threading.current_thread().name, thread.name, event, listener.__name__)
					thread.start()
				except TypeError as e:
					logging.error("%s invalid number of parameters [%s, %s]",
						threading.current_thread().name, event, listener.__name__)

	def handle(self, msg):
		c = msg.command
		if c == "PING":
			self.send("PONG", msg.params[0])
		else:
			print(msg.raw)
