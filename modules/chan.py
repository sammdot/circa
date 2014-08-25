import os
import sys

class ChannelModule:
	require = "cmd"

	def __init__(self, circa):
		self.circa = circa

		self.events = {
			"cmd.join": [self.circa.join],
			"cmd.leave": [self.leave],
			"cmd.goaway": [self.leave],
			"cmd.restart": [self.restart],
			"cmd.quit": [self.quit]
		}

	def leave(self, fr, to, text, m):
		if self.circa.is_admin(m.prefix) and fr != to:
			self.circa.part(to)

	def quit(self, fr, to, text, m):
		if self.circa.is_admin(m.prefix):
			self.circa.close()

	def restart(self, fr, to, text, m):
		if self.circa.is_admin(m.prefix):
			self.circa.close()
			os.chdir(str(self.circa.conf["cwd"]))
			os.execl(sys.executable, sys.executable, *sys.argv)

module = ChannelModule
