import logging
import client
import importlib
import modules

class Circa(client.Client):
	def __init__(self, conf):
		conf["autoconn"] = False

		for setting in "server nick username realname".split():
			if setting not in conf or conf[setting] is None:
				logging.error("Required setting %s not present", setting)
				logging.info("See %s for details", conf["log"])
				exit(1)

		client.Client.__init__(self, **conf)

		logging.info("Registering callbacks")
		self.add_listener("registered", self.registered)
		self.add_listener("invite", self.invited)

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
			importlib.reload(self.modules[name])
			return 0
		try:
			m = importlib.import_module("modules." + name).module
			if hasattr(m, "require"):
				for mod in m.require.split():
					self.load_module(mod)
			self.modules[name] = module = m(self)
			m.onload()
			return 0
		except (ImportError, AttributeError, TypeError):
			return 1

	def unload_module(self, name):
		if name not in self.modules:
			return
		m = self.modules[name]
		importlib.reload(m)
		m.onunload()
		del m
