def nicklower(nick):
	return nick.lower().replace("{", "[").replace("}", "]") \
		.replace("\\", "|").replace("~", "^")

def nickcmp(nick1, nick2):
	return nicklower(nick1) == nicklower(nick2)
