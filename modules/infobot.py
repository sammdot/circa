class InfobotModule:
	def __init__(self, circa):
		self.circa = circa

		self.listeners = {
			"message": [self.version]
		}

	def version(self, fr, to, text, msg):
		if text.lower() == "!info circa" or text.lower() == "@info circa":
			self.circa.say(to, "circa (Python/3.4) by sammi github:sammdot/circa")

module = InfobotModule
