class HelpModule:
	def __init__(self, circa):
		self.circa = circa
		self.events = {
			"cmd.help": [self.help]
		}
		self.docs = {
			"help": "help [<module>[.<command>]|$<command>] → show usage info for a command, or list all commands in a module, or list all modules"
		}

	def help(self, fr, to, msg, m):
		pfx = self.circa.conf["prefix"]
		msg = msg.split(" ", 1)[0]
		if msg:
			c = msg.split(".", 1)
			if c[0] not in self.circa.modules:
				self.circa.notice(fr, "Module {0} doesn't exist or is not loaded".format(c[0]))
				return
			module = self.circa.modules[c[0]]
			if not hasattr(module, "docs"):
				self.circa.notice(fr, "No help available for module {0}".format(c[0]))
			if len(c) == 1: # module
				if isinstance(module.docs, dict):
					commands = sorted([pfx + cmd for cmd in module.docs.keys()])
					self.circa.notice(fr, "Available commands: " + ", ".join(commands))
					self.circa.notice(fr, "Type {0}help {1}.<command> for command help.".format(pfx, c[0]))
				else:
					# in this case the module likely doesn't offer plain commands
					self.circa.notice(fr, str(module.docs))
			else: # command
				if "cmd." + c[1] not in module.events:
					self.circa.notice(fr, "No command {0}{1} in module {2}".format(pfx, c[1], c[0]))
					return
				if c[1] not in module.docs:
					self.circa.notice(fr, "No help for {0}{1} in module {2}".format(pfx, c[1], c[0]))
					return
				command = module.docs[c[1]]
				self.circa.notice(fr, pfx + command)
		else:
			modules = sorted([i for i in self.circa.modules.keys() if \
				hasattr(self.circa.modules[i], "docs")])
			self.circa.notice(fr, "Available modules: " + ", ".join(modules))
			self.circa.notice(fr, "Type {0}help <module> for a list of commands, or {0}<command> for individual command help.".format(pfx))

module = HelpModule
