import math
import operator
import re
import subprocess

class Calculator:
	"""A postfix calculator engine."""
	opers = [
		{ # no operands
		},
		{ # 1 operand
			"!": operator.not_,
		},
		{ # 2 operands
			"+": operator.add, "-": operator.sub, "*": operator.mul,
			"/": operator.truediv, "\\": operator.floordiv, "%": operator.mod,
			"**": operator.pow, "^": operator.xor, "&": operator.and_,
			"|": operator.or_,
		}
	]

	def __init__(self):
		self.stack = []

	def calc(self, expr):
		for token in expr.split():
			if token in self.opers[0]:
				self.stack.append(self.opers[0][token]())
			elif token in self.opers[1]:
				self.stack.append(self.opers[1][token](self.stack.pop()))
			elif token in self.opers[2]:
				self.stack[-2:] = [self.opers[2][token](*self.stack[-2:])]
			else:
				try:
					self.stack.append(float(token))
				except ValueError:
					pass

class CalcModule:
	require = "cmd"

	def __init__(self, circa):
		self.circa = circa
		self.contexts = {}

		self.events = {
			"cmd.dc": [self.dc],
			"cmd.dc!": [self.dc1]
		}
		self.docs = {
			"dc": "dc <expression> → execute the expression as a 'dc' command and print the result",
			"dc!": "dc! <expression> → execute the expression as a 'dc' command"
		}
	
	def dc(self, fr, to, expr, m):
		expr = re.sub(r"-([0-9])", r"_\1", expr)
		self.dc1(fr, to, expr + " p")

	def dc1(self, fr, to, expr, m):
		if to not in self.contexts:
			self.contexts[to] = None
		expr = re.sub(r"\b_\b", str(self.contexts[to]), expr)
		expr += "q\n"
		self.contexts[to] = str(subprocess.check_output(["dc", "-"],
			input=bytes(expr, "utf-8"), stderr=subprocess.STDOUT), "utf-8")
		self.circa.say(to, str(self.contexts[to]))

module = CalcModule
