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

		if line.startswith(":"):
			prefix, command, *params = line.split(" ")
			prefix = prefix[1:]
			nick = prefix.split("!")[0] if "@" in prefix else None
		else:
			command, *params = line.split(" ")

		c = [param.startswith(":") for param in params]
		if True in c:
			fc = c.index(True)
			params = params[:fc] + [" ".join(params[fc:])[1:]]

		return Message(line, nick, prefix, command, params)

