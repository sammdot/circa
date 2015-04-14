import shlex
import subprocess

from util.diff import diff

class RomajiModule:
	def __init__(self, circa):
		self.circa = circa
		self.events = {
			"cmd.romaji": [self.trans]
		}
		self.docs = {
			"romaji": "romaji [text] → Transliterates Japanese script (katakana, hiragana, kanji) into rōmaji."
		}

	def trans(self, fr, to, msg, m):
		text = shlex.quote(msg)
		out = subprocess.check_output("echo -n {0} | kakasi -i utf8 -w | " \
			"kakasi -i utf8 -Ha -Ja -Ka -Ea -ka".format(text), shell=True).decode("utf-8")
		out = out.replace(" .", ".").replace(" !", "!")
		if msg != out:
			d = diff(msg, out)
			if "\x1f" not in d:
				return
			d = d.replace("\x1f", "")
			self.circa.say(to, fr + ": " + d)

module = RomajiModule
