import subprocess

class RomajiModule:
	def __init__(self, circa):
		self.circa = circa
		self.events = {
			"message": [self.trans]
		}
		self.docs = "Automatically transliterates Japanese script in any message into rōmaji."

	def trans(self, fr, to, msg, m):
		pass

module = RomajiModule
