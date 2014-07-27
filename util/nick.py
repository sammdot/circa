import string

trans = string.maketrans("[]\\~", "{}|^")

def nicklower(nick):
	return string.translate(nick.lower(), trans)

def nickeq(nick1, nick2):
	return nicklower(nick1) == nicklower(nick2)
