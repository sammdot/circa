import logging
import client
import importlib
import modules
import sys
import time

from util.nick import nicklower
from util.mask import match
from version import version as v

class Circa(client.Client):
	version = "circa {0} http://github.com/sammdot/circa".format(".".join(map(str, v)))

	def __init__(self, conf):
		conf["autoconn"] = False

		for setting in "server nick username realname admins".split():
			if setting not in conf or conf[setting] is None:
				logging.error("Required setting %s not present", setting)
				logging.info("See %s for details", conf["log"])
				exit(1)

		self.cwd = conf["cwd"]
		self.modules = {}

		client.Client.__init__(self, **conf)
		self.conf["admins"] = set(map(nicklower, self.conf["admins"]))

		logging.info("Registering callbacks")
		self.add_listener("registered", self.registered)
		self.add_listener("invite", self.invited)
		self.add_listener("ctcp.version", self.ctcp_version)

		logging.info("Loading modules")
		sys.path.append(self.cwd)
		for module in "cmd chan module".split() + conf["modules"]:
			self.load_module(module)

		self.connect()

	def say(self, to, msg):
		msg = msg.replace("\x07", "")
		for line in msg.splitlines():
			client.Client.say(self, to, line)

	def notice(self, to, msg):
		msg = msg.replace("\x07", "")
		for line in msg.splitlines():
			client.Client.notice(self, to, line)

	def registered(self, nick, m):
		self.send("MODE", nick, "+B")
		for chan in self.conf["channels"]:
			self.join("#" + chan)
		self.server.admins = set(map(nicklower, self.conf["admins"]))

	def invited(self, chan, by, m):
		self.join(chan)

	def ctcp_version(self, fr, to):
		self.ctcp_notice(fr, "VERSION " + self.version)

	def close(self):
		self.send("QUIT")
		self.sock.close()

	def is_admin(self, prefix):
		return any(match(mask, prefix) for mask in self.server.admins)

	def load_module(self, name):
		try:
			if "modules." + name in sys.modules:
				m = importlib.reload(sys.modules["modules." + name]).module
			m = importlib.import_module("modules." + name).module
			if hasattr(m, "require"):
				for mod in m.require.split():
					self.load_module(mod)
			self.modules[name] = module = m(self)
			for event, listeners in module.events.items():
				for listener in listeners:
					self.add_listener(event, listener)
			logging.info("Loaded {0}".format(name))
		except Exception as e:
			raise Exception("Cannot import {0}: {1}".format(name, e))

	def unload_module(self, name):
		if name not in self.modules:
			return
		module = self.modules[name]
		for event, listeners in module.events.items():
			for listener in listeners:
				self.remove_listener(event, listener)
		del self.modules[name]
		logging.info("Unloaded {0}".format(name))

