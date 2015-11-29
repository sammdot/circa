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
		self.add_listener("message", self.handle_cmd)

		logging.info("Loading modules")
		sys.path.append(self.cwd)
		for module in "chan module".split() + conf["modules"]:
			self.load_module(module)

		self.connect()

	def handle_cmd(self, fr, to, text, m):
		if text.startswith(self.conf["prefix"]):
			cmd = text.split(" ")[0]
			cmdname = "$" if cmd == self.conf["prefix"] else cmd[1:]
			self.emit("cmd." + cmdname, fr, fr if to == self.nick else to,
				" ".join(text.split(" ")[1:]), m)

	def say(self, to, msg):
		lines = msg.replace("\x07", "").splitlines()
		limit = self.conf["linelimit"]
		for line in lines[:limit]:
			client.Client.say(self, to, line)
		if len(lines) > limit:
			diff = len(lines) - limit
			client.Client.say(self, to, "[... {0} more line{1}]".format(diff, "s" if diff > 1 else ""))

	def notice(self, to, msg):
		msg = msg.replace("\x07", "")
		for line in msg.splitlines():
			client.Client.notice(self, to, line)

	def registered(self, nick, m):
		self.send("MODE", nick, "+B")
		self.send("MODE", nick, "-x")
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
		if name in self.modules:
			return "{0} already loaded".format(name)
		try:
			mod = importlib.import_module("modules." + name)
			# if it's been imported before, make sure we get the latest version
			importlib.reload(mod)
			m = mod.module
			if hasattr(m, "require"):
				for mod in m.require.split():
					if mod == "cmd":
						continue
					self.load_module(mod)
			self.modules[name] = module = m(self)
			for event, listeners in module.events.items():
				for listener in listeners:
					self.add_listener(event, listener)
			logging.info("Loaded {0}".format(name))
			return 0
		except Exception as e:
			return "Cannot import {0}: {1}".format(name, e)

	def unload_module(self, name):
		if name not in self.modules:
			return
		module = self.modules[name]
		for event, listeners in module.events.items():
			for listener in listeners:
				self.remove_listener(event, listener)
		del self.modules[name]
		logging.info("Unloaded {0}".format(name))

