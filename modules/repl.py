import code
import sys
import traceback

class PythonREPLModule(code.InteractiveInterpreter):
	def __init__(self, circa):
		self.circa = circa
		self.result = ""
		code.InteractiveInterpreter.__init__(self, {"circa": self.circa})

		self.listeners = {
			"message": [self.repl]
		}

	def write(self, data):
		for line in data.split("\n"):
			line = line.rstrip()
			if len(line):
				self.circa.send("PRIVMSG", self.target, line)

	def runcode(self, cd):
		sys.stdout = self
		code.InteractiveInterpreter.runcode(self, cd)
		sys.stdout = sys.__stdout__

	def showtraceback(self):
		sys.stdout = self
		code.InteractiveInterpreter.showtraceback(self)
		sys.stdout = sys.__stdout__

	def repl(self, fr, to, text, msg):
		if fr == "sammi" and text.startswith(">>> "):
			self.target = to if to in self.circa.channels else fr
			ret = self.runsource(text.split(" ", 1)[1])
			if not ret:
				self.showtraceback()

module = PythonREPLModule
