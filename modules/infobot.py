class InfobotModule:
	def __init__(self, circa):
		self.circa = circa

		self.listeners = {
			"message": [self.version]
		}

	def version(self, fr, to, text, msg):
		if text.lower() == "!info circa":
			self.circa.say(to, "circa/0.1 (Python/3.4.0 sdirc/1.0) by sammi http://github.com/sammdot/circa")

module = InfobotModule
