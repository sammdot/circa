class ModuleModule:
	require = "cmd"

	def __init__(self, circa):
		self.circa = circa

		self.listeners = {
			"cmd.load": [self.load],
			"cmd.unload": [self.unload],
			"cmd.reload": [self.reload],
			"cmd.modules": [self.list]
		}

	def load(self, fr, to, params):
		if fr != "sammi":
			return
		l = self.circa.load_module(params[0])
		if l == 0:
			self.circa.notice(fr, "loaded " + params[0])
		elif l == 1:
			self.circa.notice(fr, "missing or invalid module: " + params[0])
		elif l == 2:
			self.circa.notice(fr, "already loaded: " + params[0])

	def unload(self, fr, to, params):
		if fr != "sammi":
			return
		l = self.circa.unload_module(params[0])
		if l == 0:
			self.circa.notice(fr, "unloaded " + params[0])
		else:
			self.circa.notice(fr, "not already loaded: " + params[0])

	def reload(self, fr, to, params):
		if fr != "sammi":
			return
		l = self.circa.unload_module(params[0])
		if l == 0:
			r = self.circa.load_module(params[0])
			if r == 0:
				self.circa.notice(fr, "reloaded " + params[0])
			elif r == 1:
				self.circa.notice(fr, "cannot reload missing or invalid module: " + params[0])
		else:
			self.load(fr, to, params)

	def list(self, fr, to, params):
		self.circa.notice(fr, "loaded modules: " + " ".join(sorted(self.circa.modules.keys())))

module = ModuleModule
