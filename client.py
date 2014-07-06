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

	def handle(self, msg):
		c = msg.command
		if c == "PING":
			self.send("PONG", msg.params[0])
		else:
			print(msg.raw)
