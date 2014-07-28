trans = str.maketrans("[]\\~", "{}|^")

def nicklower(nick):
	return nick.lower().translate(trans)

def nickeq(nick1, nick2):
	return nicklower(nick1) == nicklower(nick2)
