#!/usr/bin/env python3

import re
import socket
import threading

class Message:
	def __init__(self, line, prefix, command, params):
		self.prefix = prefix
		self.nick = prefix.split("!")[0] if prefix and "@" in prefix else None
		self.command = command
		self.params = params

	@staticmethod
	def parse(message):
		line = message.strip()
		if len(line) == 0:
			return None

		prefix, command, params = None, None, None

		if line[0] == ":":
			prefix, line = line.split(" ", 1)
			if len(prefix) == 1:
				return None
			prefix = prefix[1:]

		command, line = line.split(" ", 1)

		if line[0] == ":":
			params = [line[1:]]
		else:
			params = line.split(" ")
			try:
				first_colon = [p.startswith(":") for p in params].index(True)
			except ValueError:
				first_colon = 14
			trailing = " ".join(params[first_colon:])
			params = params[:first_colon] + [trailing]
			if len(params) and len(params[-1]):
				if params[-1][0] == ":":
					params[-1] = params[-1][1:]

		return Message(message, prefix, command, params)

class Server:
	def __init__(self, host, port):
		self.host = host
		self.port = port

		self.usermodes = set()
		self.kicklength = 0
		self.maxlist = {}
		self.maxtargets = {}
		self.modes = 3
		self.nicklength = 9
		self.topiclength = 0

		self.idlength = {}
		self.chlength = 200
		self.chlimit = {}
		self.chmodes = { "a": set(), "b": set(), "c": set(), "d": set() }
		self.types = set()

		self.prefix_mode = {}
		self.mode_prefix = {}

class Channel:
	def __init__(self, name):
		self.name = name
		self.users = {}
		self.topic = None
		self.topicby = None
		self.mode = None
		self.created = None

class Client:
	def __init__(self, **conf):
		self.sock = None
		self.nick = None
		self.server = None

		self.conf = {
			"server": None,
			"nick": None,
			"username": "sdircbot",
			"realname": "sdirc client",
			"port": 6667,
			"autorejoin": True,
			"autoconn": True,
			"channels": [],
			"prefixes": "&#"
		}

		self.conf.update(conf)

		self.nickmod = None
		self.channels = {}
		self.motd = ""

		self.listeners = {}

		if self.conf["server"] is None or self.conf["nick"] is None:
			raise Exception("server and nick required")

		self.add_listener("raw", self.parse_msg)
		self.add_listener("kick", lambda chan, who, by, reason:
			self.conf["autorejoin"] and self.join(chan))
		self.add_listener("registered", self.registered)

		if self.conf["autoconn"]:
			threading.Thread(target=self.connect).start()

	def registered(self, message):
		if self.conf["autorejoin"]:
			for c in self.conf["channels"]:
				self.join(c)

	def send(self, *msg):
		if self.sock:
			msg = list(msg)
			msg[-1] = ":" + msg[-1]
			self.sock.sendall(bytes(" ".join(map(str, msg)) + "\r\n", "utf-8"))

	def connect(self):
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.connect((self.conf["server"], self.conf["port"]))
		self.server = Server(self.conf["server"], self.conf["port"])
		self.server.types = set(self.conf["prefixes"])

		self.send("NICK", self.conf["nick"])
		self.send("USER", self.conf["username"], 8, "*", self.conf["realname"])
		self.emit("connect")

		buf = ""

		while True:
			buf += str(self.sock.recv(4096), "utf-8")
			*lines, buf = buf.split("\r\n")
			for line in lines:
				msg = Message.parse(line)
				if not msg: continue
				self.emit("raw", msg)

	def emit(self, event, *params):
		if event in self.listeners:
			for listener in self.listeners[event]:
				try:
					threading.Thread(target=lambda: listener(*params)).start()
				except TypeError:
					pass

	def add_listener(self, event, function):
		if event not in self.listeners:
			self.listeners[event] = []
		self.listeners[event].append(function)

	def remove_listener(self, event, function):
		if event in self.listeners:
			if function in self.listeners[event]:
				self.listeners[event].remove(function)

	def remove_all_listeners(self, event):
		if event in self.listeners:
			self.listeners.pop(event)

	def _handleCTCP(self, fr, to, text, type, message):
		text = text[:text.index("\x01")]
		parts = text.split()
		self.emit("ctcp", fr, to, text, type, message)
		self.emit("ctcp-" + type, fr, to, text, message)
		if type == "privmsg" and text == "VERSION":
			self.emit("ctcp-version", fr, to, message)
		if len(parts) > 1 and parts[0] == "ACTION":
			self.emit("action", fr, to, " ".join(parts[1:]), message)
		if len(parts) > 1 and parts[0] == "PING" and type == "privmsg":
			self.ctcp(fr, "notice", text)

	def join(self, channel):
		self.send("JOIN", channel)

	def part(self, channel, reason):
		self.send("PART", channel, reason)

	def notice(self, to, *params):
		self.send("NOTICE", to, *params)

	def say(self, to, msg):
		self.send("PRIVMSG", to, msg)

	def action(self, to, msg):
		self.ctcp(to, "privmsg", "ACTION " + msg)

	def ctcp(self, to, type, text):
		(self.say if type == "privmsg" else self.notice)(to, "\x01{0}\x01".format(text))

	def parse_msg(self, message):
		c = message.command
		if c == "001":
			self.nick = message.params[0]
			self.emit("registered", message)
		elif c == "004":
			self.server.usermodes = set(message.params[3])
		elif c == "005":
			for p in message.params:
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
			if self.nickmod is None:
				self.nickmod = 0
			self.nickmod += 1
			self.nick += str(self.nickmod)
			self.send("NICK", self.nick)
		elif c == "PING":
			self.send("PONG", message.params[0])
			self.emit("ping", message.params[0])
		elif c == "PONG":
			self.emit("pong", message.params[0])
		elif c == "NOTICE":
			fr, to = message.nick, message.params[0]
			text = message.params[1] or ""
			if text[0] == "\x01" and "\x01" in text[1:]:
				self._handleCTCP(fr, to, text, "notice", message)
			else:
				self.emit("notice", fr, to, text, message)
		elif c == "MODE":
			pass # TODO
		elif c == "NICK":
			if message.nick == self.nick:
				self.nick = message.params[0]
			chans = []
			for chan in self.channels:
				channel = self.channels[chan]
				channel.users[message.params[0]] = channel.users[message.nick]
				del channel.users[message.nick]
				chans.append(chan)
			self.emit("nick", message.nick, message.params[0], chans, message)
		elif c == "375":
			self.motd = message.params[1] + "\n"
		elif c == "372":
			self.motd += message.params[1] + "\n"
		elif c == "376" or c == "422":
			self.motd += message.params[1] + "\n"
			self.emit("motd", self.motd)
		elif c == "353":
			channel = self.channels[message.params[2]]
			if channel:
				users = message.params[3].strip().split()
				for user in users:
					if user[0] in self.server.prefix_mode:
						channel.users[user[1:]] = user[0]
					else:
						channel.users[user] = ""
		elif c == "366":
			channel = self.channels[message.params[1]]
			if channel:
				self.emit("names", message.params[1], channel.users)
				self.send("MODE", message.params[1])
		elif c == "332":
			channel = self.channels[message.params[1]]
			if channel:
				channel.topic = message.params[2]
		# 301, 311, 312, 313, 317, 318, 319, 330, 321, 322, 323, 333
		elif c == "TOPIC":
			self.emit("topic", message.params[0], message.params[1], message.nick, message)
			channel = self.channels[message.params[0]]
			if channel:
				channel.topic = message.params[1]
				channel.topicby = message.nick
		elif c == "324":
			channel = self.channels[message.params[1]]
			if channel:
				channel.mode = message.params[2]
		elif c == "329":
			channel = self.channels[message.params[1]]
			if channel:
				channel.created = int(message.params[2])
		elif c == "JOIN":
			chan = message.params[0]
			if self.nick == message.nick:
				self.channels[chan] = Channel(chan)
			else:
				channel = self.channels[chan]
				if channel:
					channel.users[message.nick] = ""
			self.emit("join", chan, message.nick, message)
		elif c == "PART":
			chan = message.params[0]
			self.emit("part", chan, message.nick, message)
			if self.nick == message.nick:
				self.channels.pop(chan)
			else:
				channel = self.channels[chan]
				if channel:
					del channel.users[message.nick]
		elif c == "KICK":
			chan, who, reason, *rest = message.params
			self.emit("kick", chan, who, message.nick, reason, message)
			if self.nick == message.nick:
				self.channels.pop(chan)
			else:
				channel = self.channels[chan]
				if channel:
					channel.users.pop(who)
		elif c == "KILL":
			nick = message.params[0]
			channels = []
			for chan in self.channels:
				channels.append(chan.name)
				chan.users.pop(nick)
			self.emit("kill", nick, message.params[1], channels, message)
		elif c == "PRIVMSG":
			fr, to = message.nick, message.params[0]
			text = " ".join(message.params[1:])
			if text[0] == "\x01" and "\x01" in text[1:]:
				self._handleCTCP(fr, to, text, "privmsg", message)
			else:
				self.emit("message", fr, to, text, message)
			self.emit("pm", fr, text, message)
		elif c == "INVITE":
			self.emit("invite", message.params[1], message.nick, message)
		elif c == "QUIT":
			if self.nick == message.nick:
				return
			channels = []
			for chan in self.channels:
				channels.append(chan)
				self.channels[chan].users.pop(message.nick)
			self.emit("quit", message.nick, message.params[0], channels, message)
