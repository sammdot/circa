import code
import sys

from util.nick import nickeq, nicklower

class Repl(code.InteractiveConsole):
	def __init__(self, circa, channel):
		code.InteractiveConsole.__init__(self, {"circa": circa})
		self.circa = circa
		self.channel = channel
		self.buf = ""
	
	def write(self, data):
		self.buf += data
	
	def flush(self):
		msg = self.buf.rstrip("\n")
		if len(msg) > 0:
			self.circa.say(self.channel, msg)
		self.buf = ""
	
	def run(self, code):
		sys.stdout = sys.interp = self
		self.push(code)
		sys.stdout = sys.__stdout__
		self.flush()

	def showtraceback(self):
		type, value, lasttb = sys.exc_info()
		self.circa.say(self.channel, "\x02\x034{0}\x03\x02: {1}".format( \
			type.__name__, value))

class ReplModule:
	def __init__(self, circa):
		self.circa = circa
		self.repls = {}

	def onload(self):
		self.circa.add_listener("message", self.handle_repl)

	def onunload(self):
		self.circa.remove_listener("message", self.handle_repl)

	def handle_repl(self, fr, to, text):
		if text.startswith(">>> "):
			self.repl(nicklower(fr), nicklower(fr) if nickeq(to, self.circa.nick) \
					else nicklower(to), text[len(">>> "):])

	def repl(self, fr, to, command):
		if self.circa.is_admin(fr):
			if to not in self.repls:
				self.repls[to] = Repl(self.circa, to)
			try:
				self.repls[to].run(command)
			except Exception as e:
				print(e)

module = ReplModule
