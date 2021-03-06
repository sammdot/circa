import code
import pathlib
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
		fname = pathlib.Path(lasttb.tb_frame.f_code.co_filename).name
		self.circa.say(self.channel, "\x02\x034{0}\x03\x02: {1} ({2}:{3})".format( \
			type.__name__, value, fname, lasttb.tb_lineno))

	def showsyntaxerror(self, filename):
		self.showtraceback()

class ReplModule:
	require = "cmd"

	def __init__(self, circa):
		self.circa = circa
		self.repls = {}

		self.events = {
			"message": [self.handle_repl]
		}
		self.docs = "Any message beginning with '>>> ' executes Python code. Admins only."

	def handle_repl(self, fr, to, text, m):
		if text.startswith(">>> "):
			self.repl(nicklower(fr), nicklower(fr) if nickeq(to, self.circa.nick) \
					else nicklower(to), text[len(">>> "):], m)

	def repl(self, fr, to, command, m):
		if self.circa.is_admin(m.prefix):
			if to not in self.repls:
				self.repls[to] = Repl(self.circa, to)
			self.repls[to].run(command)

module = ReplModule
