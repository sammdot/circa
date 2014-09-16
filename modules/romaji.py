import shlex
import subprocess

from util.diff import diff

class RomajiModule:
	def __init__(self, circa):
		self.circa = circa
		self.events = {
			"message": [self.trans]
		}
		self.docs = "Automatically transliterates Japanese script in any message into rōmaji."

	def trans(self, fr, to, msg, m):
		text = shlex.quote(msg)
		out = subprocess.check_output("echo -n {0} | kakasi -i utf8 -w | " \
			"kakasi -i utf8 -Ha -Ja -Ka -Ea -ka".format(text), shell=True).decode("utf-8")
		# TODO: process kakasi output
		if msg != out:
			d = diff(msg, out)
			if msg.startswith("\x01ACTION "):
				self.circa.say(to, "\x02* {0}\x02 ".format(fr) + d[len("\x01ACTION "):-1])
			else:
				self.circa.say(to, "<{0}> ".format(fr) + d)

module = RomajiModule
