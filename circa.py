import logging
import client
import importlib
import modules
import sys

from util import nicklower

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
		self.server.admins = set(map(nicklower, conf["admins"]))

		logging.info("Registering callbacks")
		self.add_listener("registered", self.registered)
		self.add_listener("invite", self.invited)

		self.load_module("cmd")

		self.connect()

	def registered(self, nick):
		self.send("UMODE2", "+B")
		if "password" in self.conf:
			self.send("PRIVMSG", "NickServ", "IDENTIFY {0}".format(
					str(self.conf["password"])))
		for chan in self.conf["channels"]:
			self.join("#" + chan)

	def invited(self, chan, by):
		self.join(chan)

	def close(self):
		self.send("QUIT")
		self.sock.close()

	def load_module(self, name):
		if name in self.modules:
			return False
		try:
			m = importlib.import_module("modules." + name).module
			if hasattr(m, "require"):
				for mod in m.require.split():
					self.load_module(mod)
			self.modules[name] = module = m(self)
			module.onload()
			return True
		except (ImportError, AttributeError, TypeError):
			return False

	def unload_module(self, name):
		if name not in self.modules:
			return
		self.modules[name].onunload()
		del sys.modules[name]
