import logging
import client
import importlib
import modules
import sys

from util.nick import nicklower
from util.mask import match

class Circa(client.Client):
	modules = {}

	def __init__(self, conf):
		conf["autoconn"] = False

		for setting in "server nick username realname admins".split():
			if setting not in conf or conf[setting] is None:
				logging.error("Required setting %s not present", setting)
				logging.info("See %s for details", conf["log"])
				exit(1)

		self.cwd = conf["cwd"]

		client.Client.__init__(self, **conf)
		self.conf["admins"] = set(map(nicklower, self.conf["admins"]))

		logging.info("Registering callbacks")
		self.add_listener("registered", self.registered)
		self.add_listener("invite", self.invited)
		self.add_listener("nick", self.chadminnick)
		self.add_listener("quit", self.rmadmin)

		logging.info("Loading modules")
		sys.path.append(self.cwd)
		self.load_module("cmd")
		self.load_module("chan")
		for module in conf["modules"]:
			self.load_module(module)

		self.connect()

	def say(self, to, msg):
		for line in msg.splitlines():
			client.Client.say(self, to, line)

	def registered(self, nick):
		self.send("UMODE2", "+B")
		if "password" in self.conf:
			self.send("PRIVMSG", "NickServ", "IDENTIFY {0}".format(
					str(self.conf["password"])))
		for chan in self.conf["channels"]:
			self.join("#" + chan)
		self.server.admins = set(map(nicklower, self.conf["admins"]))

	def invited(self, chan, by):
		self.join(chan)

	def chadminnick(self, oldnick, newnick, chans):
		if oldnick in self.server.admins:
			self.server.admins.remove(oldnick)
			self.server.admins.add(newnick)

	def rmadmin(self, nick, *args):
		if nick in self.server.admins:
			self.server.admins.remove(nick)

	def close(self):
		self.send("QUIT")
		self.sock.close()

	def is_admin(self, prefix):
		return any(match(mask, prefix) for mask in self.server.admins)

	def load_module(self, name):
		if name in self.modules:
			return False
		try:
			m = importlib.import_module("modules." + name).module
			if hasattr(m, "require"):
				for mod in m.require.split():
					self.load_module(mod)
			self.modules[name] = module = m(self)
			for event, listeners in module.events.items():
				for listener in listeners:
					self.add_listener(event, listener)
			logging.info("Loaded {0}".format(name))
			return True
		except ImportError as e:
			logging.error("Cannot import module {0}: {1}".format(name, e))
			return False
		except Exception as e:
			logging.error("Cannot load module {0}: {1}".format(name, e))
			return False

	def unload_module(self, name):
		if name not in self.modules:
			return
		module = self.modules[name]
		for event, listeners in module.events.items():
			for listener in listeners:
				self.add_listener(event, listener)
		del sys.modules["modules." + name]
