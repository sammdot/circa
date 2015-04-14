class ModuleModule:
	def __init__(self, circa):
		self.circa = circa
		self.events = {
			"cmd.load": [self.load],
			"cmd.unload": [self.unload],
			"cmd.reload": [self.reload],
			"cmd.modules": [self.modules],
		}

	def load(self, fr, to, msg, m):
		if self.circa.is_admin(m.prefix):
			module = msg.split()[0]
			r = self.circa.load_module(module)
			if r == 0:
				self.circa.notice(to, "Loaded {0}".format(module))
			else:
				self.circa.notice(to, "\x0304\x02Error\x02\x03: {0}".format(r))

	def unload(self, fr, to, msg, m):
		if self.circa.is_admin(m.prefix):
			module = msg.split()[0]
			if module not in self.circa.modules:
				return
			self.circa.unload_module(module)
			self.circa.notice(to, "Unloaded {0}".format(module))

	def reload(self, fr, to, msg, m):
		if self.circa.is_admin(m.prefix):
			module = msg.split()[0]
			if module in self.circa.modules:
				self.circa.unload_module(module)
			r = self.circa.load_module(module)
			if r == 0:
				self.circa.notice(to, "Reloaded {0}".format(module))
			else:
				self.circa.notice(to, "\x0304\x02Error\x02\x03: {0}".format(r))

	def modules(self, fr, to, msg, m):
		self.circa.notice(fr, "Available modules: " + " ".join(sorted(self.circa.modules.keys())))

module = ModuleModule

