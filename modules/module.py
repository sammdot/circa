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
			if module in self.circa.modules:
				return
			try:
				self.circa.load_module(module)
				self.circa.say(to, "Loaded {0}".format(module))
			except Exception as e:
				self.circa.say(to, "\x0304\x02Error\x02\x03: {0}".format(e))

	def unload(self, fr, to, msg, m):
		if self.circa.is_admin(m.prefix):
			module = msg.split()[0]
			if module not in self.circa.modules:
				return
			self.circa.unload_module(module)
			self.circa.say(to, "Unloaded {0}".format(module))

	def reload(self, fr, to, msg, m):
		if self.circa.is_admin(m.prefix):
			module = msg.split()[0]
			if module in self.circa.modules:
				self.circa.unload_module(module)
			try:
				self.circa.load_module(module)
				self.circa.say(to, "Reloaded {0}".format(module))
			except Exception as e:
				self.circa.say(to, "\x0304\x02Error\x02\x03: {0}".format(e))

	def modules(self, fr, to, msg, m):
		self.circa.notice(fr, "Available modules: " + " ".join(self.circa.modules.keys()))

module = ModuleModule

