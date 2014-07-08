import logging
import re
import socket
import threading

from channel import Channel, ChannelList
from message import Message
from server import Server

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
			thread = threading.Thread(name=self.conf["server"], target=self.connect)
			logging.debug("server %s", thread.name)
			thread.start()

	def connect(self):
		"""Attempt to connect to the server. Log in if successful."""

		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		try:
			self.sock.connect((self.conf["server"], self.conf["port"]))
			self.server = Server(self.conf["server"], self.conf["port"])
			logging.info("%s connected", self.server.host)

			self.send("NICK", self.conf["nick"])
			self.send("USER", self.conf["username"], 8, "*", self.conf["realname"])

			thread = threading.Thread(name=self.conf["server"] + "-listen", target=self.listen)
			logging.debug("(%s) listener %s", threading.current_thread().name, thread.name)
			thread.start()
		except socket.error as e:
			logging.error("(%s) cannot connect: %s", self.conf["server"], e)
			self.sock.close()
			self.sock = None

	def send(self, *msg):
		"""Send a raw message to the server. Prepend a colon to the last parameter."""

		if not self.sock:
			logging.error("(%s) not connected to server", self.conf["server"])
			return

		message = " ".join(map(str, msg[:-1])) + " :" + str(msg[-1])
		self.sock.sendall(bytes(message + "\r\n", "utf-8"))
		logging.debug("(%s) %s", threading.current_thread().name, message.rstrip())

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
			logging.error("(%s) not connected to server", self.conf["server"])
			return

		buf = ""
		while True:
			buf += str(self.sock.recv(4096), "utf-8")
			*msgs, buf = buf.split("\r\n")
			for msg in msgs:
				m = Message.parse(msg)
				thread = threading.Thread(target=lambda: self.handle(m))
				logging.debug("(%s) handler thread %s [%s]",
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
					logging.debug("(%s) worker thread %s [%s, %s]",
						threading.current_thread().name, thread.name, event, listener.__name__)
					thread.start()
				except TypeError as e:
					logging.error("(%s) invalid number of parameters [%s, %s]",
						threading.current_thread().name, event, listener.__name__)

	def _ctcp(self, fr, to, text, type):
		text = text[1:text.index("\x01")]
		parts = text.split()
		self.emit("ctcp", fr, to, text, type)
		self.emit("ctcp." + type, fr, to, text)

		if type == "privmsg":
			if text == "VERSION":
				self.emit("ctcp.version", fr, to)
			elif len(parts) > 1 and parts[0] == "ACTION":
				self.emit("action", fr, to, " ".join(parts[1:]))
			elif len(parts) > 1 and parts[0] == "PING":
				self.ctcp(fr, "notice", "PONG " + " ".join(parts[1:]))

	def handle(self, msg):
		c = msg.command
		if c == "001":
			self.nick = self.conf["nick"] + self.nickmod * "_"
			self.emit("registered", msg.params[0])
		elif c == "004":
			self.server.usermodes = set(msg.params[3])
		elif c == "005":
			for p in msg.params:
				if "=" in p:
					param, value = p.split("=")
					if param == "CHANLIMIT":
						for pair in value.split(","):
							typ, num = pair.split(":")
							self.server.chlimit[typ] = int(num)
					elif param == "CHANMODES":
						modes = value.split(",")
						self.server.chmodes = dict(zip("abcd", map(set, modes)))
					elif param == "CHANTYPES":
						self.server.types = set(value)
					elif param == "CHANNELLEN":
						self.server.chlength = int(value)
					elif param == "IDCHAN":
						for pair in value.split(","):
							typ, num = pair.split(":")
							self.server.idlength[typ] = int(num)
					elif param == "KICKLEN":
						self.server.kicklength = int(value)
					elif param == "NICKLEN":
						self.server.nicklength = int(value)
					elif param == "PREFIX":
						if re.match(r"^\((.*)\)(.*)$", value):
							modes = value.split(")")[0][1:]
							prefixes = value.split(")")[1]

							self.server.prefix_mode = dict(zip(prefixes, modes))
							self.server.mode_prefix = dict(zip(modes, prefixes))

							self.server.chmodes["b"].update(modes)
					elif param == "TARGMAX":
						for pair in value.split(","):
							typ, num = pair.split(":")
							self.server.maxtargets[typ] = int(num) if num else 0
					elif param == "TOPICLEN":
						self.server.topiclength = int(value)
		elif c == "433":
			self.nickmod += 1
			self.send("NICK", self.conf["nick"] + self.nickmod * "_")
		elif c == "PING":
			self.send("PONG", msg.params[0])
			self.emit("ping", msg.params[0])
		elif c == "PONG":
			self.emit("pong", msg.params[0])
		elif c == "NOTICE":
			fr, to = msg.nick, msg.params[0]
			text = msg.params[1] or ""
			if text[0] == "\x01" and "\x01" in text[1:]:
				self._ctcp(fr, to, text, "notice")
			else:
				self.emit("notice", fr, to, text)
		elif c == "MODE":
			pass # TODO
		elif c == "NICK":
			nick = msg.params[0]
			if msg.nick == self.nick:
				self.nick = nick
			chans = [i.name for i in filter(lambda c: msg.nick in c, self.channels.values())]
			for chan in self.channels.values():
				chan.users[nick] = chan.users[msg.nick]
				chan.users.pop(nick)
			self.emit("nick", msg.nick, nick, chans)

		else:
			print(msg.raw)
