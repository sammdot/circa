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
		out = subprocess.check_output("echo {0} | iconv -f utf8 -t eucjp | kakasi -i euc -w | " \
			"kakasi -i euc -Ha -Ja -Ka -Ea -ka".format(text), shell=True).decode("utf-8")
		self.circa.say(to, diff(text, out))

module = RomajiModule
