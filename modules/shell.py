import subprocess

class ShellModule:
	def __init__(self, circa):
		self.circa = circa

		self.listeners = {
			"message": [self.shell]
		}

	def shell(self, fr, to, text, msg):
		if fr == "sammi" and text.startswith("$ "):
			pass

module = ShellModule
