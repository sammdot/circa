import functools
import math
import operator
import random
import re
import time

class Calculator:
	"""A postfix calculator engine."""
	opers = [
		{ # no operands
			"time": lambda: int(time.time()),
			"rand": lambda: random.random(),
			"e": lambda: math.e, "pi": lambda: math.pi, "i": lambda: 1j
		},
		{ # 1 operand
			"~": lambda x: ~x, "sqrt": math.sqrt, "ln": math.log, "log": math.log10,
			"sin": math.sin, "cos": math.cos, "tan": math.tan, "exp": math.exp,
			"asin": math.asin, "acos": math.acos, "atan": math.atan,
			"rad": math.radians, "deg": math.degrees, "floor": math.floor,
			"ceil": math.ceil, "abs": math.fabs, "!": math.factorial,
			"1/x": lambda x: 1/x, "inv": lambda x: 1/x,
		},
		{ # 2 operands
			"+": operator.add, "-": operator.sub, "*": operator.mul,
			"/": operator.truediv, "\\": operator.floordiv, "%": operator.mod,
			"**": operator.pow, "^": operator.xor, "&": operator.and_,
			"|": operator.or_, ">>": operator.rshift, "<<": operator.lshift,
		}
	]
	opers_ = {
		"_": lambda self: self.dup(),
		"@>": lambda self: self.sort(),
		"@<": lambda self: self.sort(True),
		"@+": lambda self: self.sum(),
		"@*": lambda self: self.product(),
		"->": lambda self: self.range(),
		"d": lambda self: self.random(),
	}
	bases = {"b": 2, "o": 8, "h": 16, "x": 16}

	def __init__(self):
		self.stack = []

	def dup(self):
		self.stack.append(self.stack[-1])
	def sort(self, rev=False):
		self.stack = sorted(self.stack, reverse=rev)
	def sum(self):
		self.stack = [sum(self.stack)]
	def product(self):
		self.stack = [functools.reduce(operator.mul, self.stack, 1)]
	def range(self):
		to, fr = self.stack.pop(), self.stack.pop()
		self.stack.extend(range(fr, to + 1) if to > fr else range(to, fr + 1)[::-1])
	def random(self):
		b, a = self.stack.pop(), self.stack.pop()
		self.stack.extend([random.randint(1, b) for i in range(a)])

	def calc(self, expr):
		self.stack = []
		for token in expr.split():
			if token in self.opers[0]:
				self.stack.append(self.opers[0][token]())
			elif token in self.opers[1]:
				self.stack.append(self.opers[1][token](self.stack.pop()))
			elif token in self.opers[2]:
				self.stack[-2:] = [self.opers[2][token](*self.stack[-2:])]
			elif token in self.opers_:
				self.opers_[token](self)
			elif len(token.split("/")) == 2:
				t = token.split("/")
				try:
					self.stack.append(int(t[0]) / int(t[1]))
				except ValueError:
					pass
			else:
				try:
					val = None
					if token[-1] in self.bases:
						val = int(token[:-1], self.bases[token[-1]])
					elif len(token) > 2 and token[0] == "0" and token[1] in self.bases:
						val = int(token[2:], self.bases[token[1]])
					else:
						val = float(token)
						if val.is_integer():
							val = int(val)
					self.stack.append(val)
				except ValueError:
					pass
		self.stack = [int(i) if float(i).is_integer() else i for i in self.stack]

class CalcModule:
	require = "cmd"

	def __init__(self, circa):
		self.circa = circa
		self.contexts = {}

		self.events = {
			"cmd.calc": [self.calc],
			"cmd.bcalc": [self.bcalc],
			"cmd.ocalc": [self.ocalc],
			"cmd.hcalc": [self.hcalc],
		}
		self.docs = {
			"calc": "calc [expr] → evaluate the postfix expression. More info in the online docs.",
			"bcalc": "bcalc [expr] → like calc, but returns answers in binary",
			"ocalc": "ocalc [expr] → like calc, but returns answers in octal",
			"hcalc": "hcalc [expr] → like calc, but returns answers in hexadecimal",
		}

	def ensure_context(self, chan):
		if chan not in self.contexts:
			self.contexts[chan] = Calculator()

	def _calc(self, to, expr):
		self.ensure_context(to)
		self.contexts[to].calc(expr)
		return self.contexts[to].stack

	def calc(self, fr, to, expr, m):
		results = self._calc(to, expr)
		self.circa.say(to, fr + ": " + ", ".join(map(str, results)))

	def bcalc(self, fr, to, expr, m):
		results = map(lambda x: bin(x)[2:] + "b", self._calc(to, expr))
		self.circa.say(to, fr + ": " + ", ".join(map(str, results)))

	def ocalc(self, fr, to, expr, m):
		results = map(lambda x: oct(x)[2:] + "o", self._calc(to, expr))
		self.circa.say(to, fr + ": " + ", ".join(map(str, results)))

	def hcalc(self, fr, to, expr, m):
		results = map(lambda x: hex(x)[2:].upper() + "h", self._calc(to, expr))
		self.circa.say(to, fr + ": " + ", ".join(map(str, results)))

module = CalcModule
