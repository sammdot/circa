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
		pass

module = HelpModule
