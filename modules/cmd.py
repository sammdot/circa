class CommandModule:
	def __init__(self, circa):
		self.circa = circa

		self.listeners = {
			"message": [self.command]
		}

	def command(self, fr, to, text):
		if text.startswith(self.circa.conf["prefix"]):
			cmd, *params = text.split()
			self.circa.emit("cmd." + cmd[1:], fr, to, params)

module = CommandModule
