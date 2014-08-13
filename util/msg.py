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
			prefix, command = line.split(" ", 1)
			prefix = prefix[1:]
			nick = prefix.split("!")[0] if "@" in prefix else None
		else:
			command = line

		command, *trail = command.split(" :", 1)
		command, *params = command.split(" ")
		params.extend(trail)

		return Message(line, nick, prefix, command, params)

