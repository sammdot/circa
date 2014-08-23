import re
import string

"""
The 'tr' implementation was based on github:ikegami-yukino/python-tr.
"""

all = [chr(i) for i in range(256)]

def mklist(src):
	src = src.replace("\\/", "/") \
		.replace("[:upper:]", string.ascii_uppercase) \
		.replace("[:lower:]", string.ascii_lowercase) \
		.replace("[:alpha:]", string.ascii_letters) \
		.replace("[:digit:]", string.digits) \
		.replace("[:xdigit:]", string.hexdigits) \
		.replace("[:alnum:]", string.digits + string.ascii_letters) \
		.replace("[:blank:]", string.whitespace) \
		.replace("[:punct:]", string.punctuation) \
		.replace("[:cntrl:]", "".join([i for i in all if i not in string.printable])) \
		.replace("[:print:]", string.printable)
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
	return "".join([chr(i) for i in lst])

def squeeze(lst, src):
	for ch in lst:
		src = re.sub(ch + r"{2,}", ch, src)
	return src

def tr(frm, to, src):
	return src.translate(str.maketrans(frm, to))

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
				msgs = [line for line in msgs if search.lower() in line.lower()]
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
			lhslst = mklist(lhs)
			rhslst = mklist(rhs)
			find = [c.lower() for c in all if c not in lhslst] if "c" in flags else lhslst
			msgs = [line for line in msgs if len(set(line.lower()) & set(find))]
			if len(msgs):
				u = msgs[0]
				t = u[len("\x01ACTION "):] if u.startswith("\x01ACTION ") else u
				rhs = unescape(rhs.replace("\\/", "/"))
				if "d" in flags:
					todel = lhslst[len(rhslst):]
					lhslst = lhslst[:len(rhslst)]
					t = "".join([c for c in t if c not in todel])
				else:
					if len(rhslst) < len(lhslst):
						rhslst += "".join([rhslst[-1]] * (len(lhslst) - len(rhslst)))
					else:
						rhslst = rhslst[:len(lhslst)]
				t = tr(lhslst, rhslst, t)
				if "s" in flags:
					t = squeeze(rhslst, t)
				if u.startswith("\x01ACTION "):
					t = t.replace("\x01", "")
					self.circa.say(to, "\x02* {0}\x02 {1}".format(user, t))
				else:
					self.circa.say(to, "<{0}> {1}".format(user, t))

module = SedModule
