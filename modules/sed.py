import re
import string

from util.esc import unescape

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
			target, search, lhs, rhs, flags = match.groups()
			user = target or fr
			msgs = self.circa.channels[to[1:]].users[user].messages[::-1]
			msgs = [line for line in msgs if not self.subre.match(line)]
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
			target, search, lhs, rhs, flags = match.groups()
			user = target or fr
			msgs = self.circa.channels[to[1:]].users[user].messages[::-1]
			msgs = [line for line in msgs if not self.trre.match(line)]
			if search:
				msgs = [line for line in msgs if search.lower() in line.lower()]
			lhslst = mklist(lhs)
			rhslst = unescape(mklist(rhs.replace("\\/", "/")).replace("\\", "\\\\"))
			find = [c for c in all if c not in lhslst] if "c" in flags else lhslst
			msgs = [line for line in msgs if len(set(line) & set(find))]
			if len(msgs):
				u = msgs[0]
				t = u[len("\x01ACTION "):] if u.startswith("\x01ACTION ") else u
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
