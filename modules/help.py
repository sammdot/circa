class HelpModule:
	def __init__(self, circa):
		self.circa = circa
		self.events = {
			"cmd.help": [self.help]
		}
		self.docs = {
			"help": "help <module>[.<command>] → show usage info for a command, or list all commands in a module"
		}

	def help(self, fr, to, msg, m):
		print(msg)
		msg = msg.split(" ", 1)
		if msg:
			...
		else:
			modules = [i for i in self.circa.modules.keys()	if hasattr(self.circa.modules[i], "docs")]
			self.circa.say(to, "Available modules: " + " ".join(modules))

module = HelpModule
