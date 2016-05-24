import difflib

def diff(a, b):
	sm = difflib.SequenceMatcher(None, a, b)
	out = []
	for opcode, a0, a1, b0, b1 in sm.get_opcodes():
		if opcode == "equal":
			out.append(sm.a[a0:a1])
		elif opcode == "insert":
			out.append("\x16" + sm.b[b0:b1] + "\x16")
		elif opcode == "delete":
			pass
		elif opcode == "replace":
			out.append("\x16" + sm.b[b0:b1] + "\x16")
		else:
			raise RuntimeError("unknown opcode")
	return "".join(out)

