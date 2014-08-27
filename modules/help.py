class HelpModule:
	def __init__(self, circa):
		self.circa = circa
		self.events = {
			"cmd.help": [self.help]
		}
		self.docs = {
			"help": "help [<module>[.<command>]] → show usage info for a command, or list all commands in a module, or list all modules"
		}

	def help(self, fr, to, msg, m):
		msg = msg.split(" ", 1)[0]
		if msg:
			c = msg.split(".", 1)
			module = self.circa.modules[c[0]]
			if len(c) == 1: # module
				if isinstance(module.docs, dict):
					commands = sorted(module.docs.keys())
					self.circa.say(to, "Available commands: " + " ".join(commands))
				else:
					# in this case the module likely doesn't offer plain commands
					self.circa.say(to, str(module.docs))
			else: # command
				command = module.docs[c[1]]
				self.circa.say(to, self.circa.conf["prefix"] + command)
		else:
			modules = sorted([i for i in self.circa.modules.keys() if \
				hasattr(self.circa.modules[i], "docs")])
			self.circa.say(to, "Available modules: " + " ".join(modules))

module = HelpModule
