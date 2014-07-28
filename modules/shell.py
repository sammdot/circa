import subprocess

class ShellModule:
	def __init__(self, circa):
		self.circa = circa

	def onload(self):
		self.circa.add_listener("message", self.shell)

	def onunload(self):
		self.circa.remove_listener("message", self.shell)

	def shell(self, fr, to, msg):
		if msg.startswith("$ ") and self.circa.is_admin(fr):
			try:
				stdout = subprocess.check_output(["/bin/bash", "-c", msg[2:]],
					stderr=subprocess.STDOUT)
				self.circa.say(to, str(stdout, "utf-8"))
			except subprocess.CalledProcessError as e:
				self.circa.say(to, str(e.output, "utf-8"))
				self.circa.say(to, "\x034Return code {0}\x03" \
					.format(e.returncode))

module = ShellModule
