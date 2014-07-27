import string

def nicklower(nick):
	return string.translate(nick.lower(), string.maketrans("[]\\~", "{}|^")

def nickeq(nick1, nick2):
	return nicklower(nick1) == nicklower(nick2)
