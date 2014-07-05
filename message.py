class Message:
	def __init__(self, line, nick, prefix, command, params):
		self.raw = line
		self.nick = nick
		self.prefix = prefix
		self.command = command
		self.params = params

	@staticmethod
	def parse(line):
		if len(line.strip()) == 0:
			return None

		params = []
		nick, prefix, command = None, None, None

		if line[0] == ":":
			prefix, command, *params = line.split(" ")
			prefix = prefix[1:]
			nick = prefix.split("!")[0] if "@" in prefix else None
		else:
			command, *params = line.split(" ")

		colons = [param.startswith(":") for param in params]
		if True in colons:
			fcol = colons.index(True)
			params = params[:fcol] + [" ".join(params[fcol:])[1:]]

		return Message(line, nick, prefix, command, params)
