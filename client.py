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
			threading.Thread(name="main", target=self.connect).start()
	
	def connect(self):
		"""Attempt to connect to the server. Log in if successful."""

		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		try:
			self.sock.connect((self.conf["server"], self.conf["port"]))
			self.server = Server(self.conf["server"], self.conf["port"])
			logging.info("Connected to %s", self.server.host)

			self.send("NICK", self.conf["nick"])
			self.send("USER", self.conf["username"], 8, "*", \
				self.conf["realname"])

			threading.Thread(name="listen", target=lambda: self.listen).start()
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

	def listen(self):
		"""Listen for incoming messages from the IRC server."""
		if not self.sock:
			logging.error("Not connected to server")
			return
		
		buf = ""
		while True:
			try:
				buf += str(self.sock.recv(4096), "utf-8")
				*msgs, buf = buf.split("\r\n")
				for msg in msgs:
					m = Message.parse(msg)
					thread = threading.Thread(target=lambda: self.handle(m))
					logging.debug("(%s) handler thread %s [%s]",
						threading.current_thread().name, thread.name, m.command)
					thread.start()
			except socket.error:
				logging.info("Disconnected from server")
				self.sock.close()
				self.sock = None
				break
	
	def add_listener(self, event, fn):
		"""Add a function to listen for the specified event."""
		if event not in self.listeners:
			self.listeners[event] = []
		self.listeners[event].append(fn)
	
	def remove_listener(self, event, fn):
		"""Remove a function as a listener from the specified event."""
		if event not in self.listeners:
			return
		self.listeners[event] = [l for l in self.listeners[event] if l != fn]
	
	def remove_listeners(self, event):
		"""Remove all functions listening for the specified event."""
		if event not in self.listeners:
			return
		self.listeners.pop(event)
	
	def emit(self, event, *params):
		"""Emit an event, and call all functions listening for it."""
		if event in self.listeners:
			for listener in self.listeners[event]:
				try:
					thread = threading.Thread(target=lambda: listener(*params))
					logging.debug("(%s) worker thread %s [%s, %s]",
						threading.current_thread().name, thread.name, event,
						listener.__name__)
					thread.start()
				except TypeError as e:
					logging.error("(%s) invalid number of parameters [%s]",
						threading.current_thread().name, listener.__name__)

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
				self.ctcp_notice(fr, "PONG " + " ".join(parts[1:]))

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
			chans = [i.name for i in filter(lambda c: msg.nick in c, \
				self.channels.values())]
			for chan in self.channels.values():
				chan.users[nick] = chan.users[msg.nick]
				chan.users.pop(nick)
			self.emit("nick", msg.nick, nick, chans)
		elif c == "375":
			self.server.motd = msg.params[1] + "\n"
		elif c == "372":
			self.server.motd += msg.params[1] + "\n"
		elif c == "376" or c == "422":
			self.server.motd += msg.params[1] + "\n"
			self.emit("motd", self.server.motd)
		elif c == "353":
			channel = self.channels[msg.params[2][1:]]
			if channel:
				users = msg.params[3].strip().split()
				for user in users:
					if user[0] in self.server.prefix_mode:
						channel.users[user[1:]] = user[0]
					else:
						channel.users[user] = ""
		elif c == "366":
			channel = self.channels[msg.params[1][1:]]
			if channel:
				self.emit("names", msg.params[1], channel.users)
				self.send("MODE", msg.params[1])
		elif c == "332":
			channel = self.channels[msg.params[1][1:]]
			if channel:
				channel.topic = msg.params[2]
		# 301, 311, 312, 313, 317, 318, 319, 330, 321, 322, 323, 333
		elif c == "TOPIC":
			self.emit("topic", msg.params[0], msg.params[1], msg.nick, msg)
			channel = self.channels[msg.params[0][1:]]
			if channel:
				channel.topic = msg.params[1]
				channel.topicby = msg.nick
		elif c == "324":
			channel = self.channels[msg.params[1][1:]]
			if channel:
				channel.mode = msg.params[2]
		elif c == "329":
			channel = self.channels[msg.params[1][1:]]
			if channel:
				channel.created = int(msg.params[2])
		elif c == "JOIN":
			chan = msg.params[0]
			if self.nick == msg.nick:
				self.channels[chan[1:]] = Channel(chan)
			else:
				channel = self.channels[chan[1:]]
				if channel:
					channel.users[msg.nick] = ""
			self.emit("join", chan, msg.nick)
		elif c == "PART":
			chan = msg.params[0]
			self.emit("part", chan, msg.nick)
			if self.nick == msg.nick:
				self.channels.pop(chan)
			else:
				channel = self.channels[chan]
				if channel:
					del channel.users[msg.nick]
		elif c == "KICK":
			chan, who, reason, *rest = msg.params
			self.emit("kick", chan, who, msg.nick, reason)
			if self.nick == msg.nick:
				self.channels.pop(chan)
			else:
				channel = self.channels[chan]
				if channel:
					channel.users.pop(who)
		elif c == "KILL":
			nick = msg.params[0]
			channels = []
			for chan in self.channels:
				channels.append(chan.name)
				chan.users.pop(nick)
			self.emit("kill", nick, msg.params[1], channels)
		elif c == "PRIVMSG":
			fr, to = msg.nick, msg.params[0]
			text = " ".join(msg.params[1:])
			if text[0] == "\x01" and "\x01" in text[1:]:
				self._ctcp(fr, to, text, "privmsg")
			else:
				self.emit("message", fr, to, text)
			self.emit("pm", fr, text, msg)
		elif c == "INVITE":
			self.emit("invite", msg.params[1], msg.nick)
		elif c == "QUIT":
			if self.nick == msg.nick:
				return
			channels = []
			for chan in self.channels:
				if msg.nick in self.channels[chan]:
					channels.append(chan.name)
					self.channels[chan].users.pop(msg.nick)
			self.emit("quit", msg.nick, msg.params[0], channels)
