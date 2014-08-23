import re

"""
The 'tr' implementation was based on github:ikegami-yukino/python-tr.
"""

def mklist(src):
	src = src.replace("\\/", "/")
	lst = []
	bs = False
	hy = False
	for ch in src:
		if ch == "\\":
			if not bs: bs = True
			continue
		elif ch == "-" and not bs:
			hy = True
			continue
		elif hy:
			lst.extend(range(lst[-1] + 1, ord(ch)))
		lst.append(ord(ch))
		bs = False
		hy = False
	return lst

def mkchar(lst):
	return list(map(chr, lst))

def squeeze(lst, src):
	for ch in lst:
		src = re.sub(ch + r"{2,}", ch, sub)
	return src

def tr(frm, to, src):
	return src.translate(dict(zip(frm, to)))

def unescape(text):
	"""Unescape function based on http://stackoverflow.com/a/15528611."""
	regex = re.compile(b'\\\\(\\\\|[0-7]{1,3}|x.[0-9a-f]?|[\'"abfnrt]|.|$)')
	def replace(m):
		b = m.group(1)
		if len(b) == 0:
			raise ValueError("Invalid character escape: '\\'.")
		i = b[0]
		if i == 120:
			v = int(b[1:], 16)
		elif 48 <= i <= 55:
			v = int(b, 8)
		elif i == 34: return b'"'
		elif i == 39: return b"'"
		elif i == 92: return b'\\'
		elif i == 97: return b'\a'
		elif i == 98: return b'\b'
		elif i == 102: return b'\f'
		elif i == 110: return b'\n'
		elif i == 114: return b'\r'
		elif i == 116: return b'\t'
		else:
			s = b.decode('ascii')
			raise UnicodeDecodeError(
				'stringescape', text, m.start(), m.end(), "Invalid escape: %r" % s
			)
		return bytes((v, ))
	result = regex.sub(replace, bytes(text, "utf-8"))
	return str(result, "utf-8")

class SedModule:
	subre = re.compile(r"^(?:(\S+)[:,]\s)?(?:s|(.+?)/s)/((?:\\/|[^/])+)\/((?:\\/|[^/])*?)/([gixs]{0,4})?(?: .*)?$")
	trre = re.compile("^(?:(\S+)[:,]\s)?(?:y|(.+?)/y)/((?:\\/|[^/])+)\/((?:\\/|[^/])*?)/([cds]{0,3})?(?: .*)?$")

	def __init__(self, circa):
		self.circa = circa
		self.events = {
			"message": [self.sub, self.tr]
		}

	def sub(self, fr, to, msg, m):
		match = self.subre.match(msg)
		if match:
			self.circa.channels[to[1:]].users[fr].messages.pop()
			target, search, lhs, rhs, flags = match.groups()
			user = target or fr
			msgs = self.circa.channels[to[1:]].users[user].messages[::-1]
			if search:
				msgs = [line for line in msgs if search in line]
			msgs = [line for line in msgs if re.search(lhs, line)]
			if len(msgs):
				u = msgs[0]
				f = 0
				if "i" in flags: f |= re.I
				if "x" in flags: f |= re.X
				if "s" in flags: f |= re.S
				rhs = rhs.replace("\\/", "/")
				rhs = re.sub(r"(?<!\\)(\\)(?=\d+|g<\w+>)", r"\\\\", rhs)
				rhs = unescape(rhs)
				count = int("g" not in flags)
				t = u[len("\x01ACTION "):] if u.startswith("\x01ACTION ") else u
				t = re.sub(lhs, rhs, t, count=count, flags=f)
				if u.startswith("\x01ACTION ") or t.startswith("\x01ACTION "):
					if t.startswith("\x01ACTION "):
						t = t[len("\x01ACTION "):]
					t = t.replace("\x01", "")
					self.circa.say(to, "\x02* {0}\x02 {1}".format(user, t))
				else:
					self.circa.say(to, "<{0}> {1}".format(user, t))

	def tr(self, fr, to, msg, m):
		match = self.trre.match(msg)
		if match:
			self.circa.channels[to[1:]].users[fr].messages.pop()
			target, search, lhs, rhs, flags = match.groups()
			user = target or fr
			msgs = self.circa.channels[to[1:]].users[user].messages[::-1]
			if search:
				msgs = [line for line in msgs if search in line]
			lhslst = mkchar(mklist(lhs))
			msgs = [line for line in msgs if len(set(line) & set(lhslst))]
			if len(msgs):
				t = msgs[0]

module = SedModule
