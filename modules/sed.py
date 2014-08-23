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
				t = msgs[0]
				f = 0
				if "i" in flags: f |= re.I
				if "x" in flags: f |= re.X
				if "s" in flags: f |= re.S
				rhs = rhs.replace("\\/", "/")
				count = int("g" not in flags)
				if t.startswith("\x01ACTION "):
					t = t[len("\x01ACTION "):-1]
					t = re.sub(lhs, rhs, t, count=count, flags=f)
					self.circa.say(to, "\x02* {0}\x02 {1}".format(user, t))
				else:
					t = re.sub(lhs, rhs, t, count=count, flags=f)
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
