class CommandModule:
	def __init__(self, circa):
		self.circa = circa

	def onload(self):
		self.circa.add_listener("message", self.handle_cmd)

	def onunload(self):
		self.circa.remove_listener("message", self.handle_cmd)

	def handle_cmd(self, fr, to, text):
		if text.startswith(self.circa.conf["prefix"]):
			cmd = text.split(" ")[0]
			cmdname = "$" if cmd == self.circa.conf["prefix"] else cmd[1:]
			self.circa.emit("cmd." + cmdname, fr, fr if to == self.circa.nick else to,
				" ".join(text.split(" ")[1:]))

module = CommandModule
