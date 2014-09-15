import difflib

def diff(a, b):
	sm = difflib.SequenceMatcher(a, b)
	out = []
	for opcode, a0, a1, b0, b1 in sm.get_opcodes():
		if opcode == "equal":
			out.append(seqm.a[a0:a1])
		elif opcode == "insert":
			out.append("\x1f" + seqm.b[b0:b1] + "\x1f")
		elif opcode == "delete":
			pass
		elif opcode == "replace":
			raise NotImplementedError("encountered 'replace' opcode")
		else:
			raise RuntimeError("unknown opcode")
	return "".join(out)

