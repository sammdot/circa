#!/usr/bin/env python3

from client import Client
import yaml
import logging
import threading
import importlib
import modules

VERSION = "1.0"

class Circa(Client):
	def __init__(self, **conf):
		conf["autoconn"] = False
		conf["prefix"] = conf["prefix"] if "prefix" in conf else "\\"
		Client.__init__(self, **conf)

		self.modules = {}

		self.add_listener("registered",
			lambda m: (self.send("UMODE2", "+B"), self.say("groupserv", "join !bots")))
		for module in "cmd module leave".split() + self.conf["modules"]:
			self.load_module(module)

		self.add_listener("invite", lambda to, by, m: self.join(to))
		self.add_listener("ctcp-version", self.version)

		self.connect()

	def version(self, fr, to, msg):
		self.notice(fr, "\x01VERSION circa {0}\x01".format(VERSION))

	@staticmethod
	def wrap(line):
		words = []

		width = 80
		for word in line.split():
			if len(word) + 1 > width:
				words.append("\xFF")
				width = 80 - len(word)
			else:
				width = width - len(word) - 1
			words.append(word)

		line2 = " ".join(words)
		sublines = line2.split(" \xFF ")
		return sublines

	def say(self, to, msg, wrap=True):
		msg = [line.rstrip() for line in msg.split("\n")]
		for line in msg:
			for subline in (Circa.wrap(line) if wrap else line):
				Client.say(self, to, subline)

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

		return 0

if __name__ == "__main__":
	try:
		logging.basicConfig(filename="circa.log", style="%",
		                    format="%(asctime)s %(levelname)s %(message)s",
		                    level=logging.DEBUG)
		file = open("config.yaml")
		config = yaml.load(file)
		file.close()
		for c in config:
			threading.Thread(target=lambda: Circa(**c)).start()
	except KeyboardInterrupt:
		print("Bye")

