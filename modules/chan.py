import os
import sys
import shutil

class ChannelModule:
	require = "cmd"

	def __init__(self, circa):
		self.circa = circa

		self.events = {
			"cmd.join": [self.join],
			"cmd.leave": [self.leave],
			"cmd.goaway": [self.goaway],
			"cmd.restart": [self.restart],
			"cmd.quit": [self.quit]
		}
		self.docs = {
			"join": "join <channel>, ... → join the specified channels. Admins only.",
			"leave": "leave [channel] → leave the channel (defaults to the current channel). Admins only.",
			"goaway": "goaway → leave the current channel. Admins only.",
			"restart": "restart → restart the client. Admins only.",
			"quit": "quit → disconnect from IRC. Admins only."
		}

	def join(self, fr, to, text, m):
		if self.circa.is_admin(m.prefix):
			chans = [ch.strip() for ch in text.split(",")]
			for chan in chans:
				self.circa.join(chan)

	def leave(self, fr, to, text, m):
		if self.circa.is_admin(m.prefix):
			if text.strip():
				chan = text.strip().split()[0]
				self.circa.part(chan)
			elif fr != to:
				self.circa.part(to)

	def goaway(self, fr, to, text, m):
		if self.circa.is_admin(m.prefix) and fr != to:
			self.circa.part(to)

	def quit(self, fr, to, text, m):
		if self.circa.is_admin(m.prefix):
			self.circa.close()

	def restart(self, fr, to, text, m):
		if self.circa.is_admin(m.prefix):
			self.circa.close()
			os.chdir(str(self.circa.conf["cwd"]))
			shutil.rmtree("__pycache__")
			os.execl(sys.executable, sys.executable, *sys.argv)

module = ChannelModule
