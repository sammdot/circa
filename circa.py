#!/usr/bin/env python3

import sdirc
import yaml
import threading
import importlib
import modules

class Circa(sdirc.Client):
	def __init__(self, **conf):
		conf["autoconn"] = False
		sdirc.Client.__init__(self, **conf)

		self.modules = {}

		self.add_listener("registered", lambda m: self.send("UMODE2", "+B"))
		for module in "cmd module leave".split() + self.conf["modules"]:
			self.load_module(module)

		self.add_listener("invite", lambda to, by, m: self.join(to))

		self.connect()

	def say(self, to, msg):
		msg = [line.rstrip() for line in msg.split("\n")]
		for line in msg:
			sdirc.Client.say(self, to, line)

	def load_module(self, name):
		if name in self.modules:
			return 2

		try:
			m = importlib.import_module("modules." + name).module
			if hasattr(m, "require"):
				for mod in m.require.split():
					self.load_module(mod)
			self.modules[name] = module = m(self)
			for event, listeners in module.listeners.items():
				for listener in listeners:
					self.add_listener(event, listener)
			return 0
		except ImportError:
			return 1
		except AttributeError:
			return 1
		except TypeError:
			return 1

	def unload_module(self, name):
		if name not in self.modules:
			return 1

		module = self.modules[name]
		for event, listeners in module.listeners.items():
			for listener in listeners:
				self.remove_listener(event, listener)

		del self.modules[name]
		self.modules.pop(name)

		return 0

if __name__ == "__main__":
	try:
		file = open("config.yaml")
		config = yaml.load(file)
		file.close()
		for c in config:
			threading.Thread(target=lambda: Circa(**c)).start()
	except KeyboardInterrupt:
		print("Bye")
