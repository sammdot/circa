import cmath
import functools
import math
import operator
import random
import re
import time

class StackUnderflow(Exception):
	pass

class Calculator:
	"""A postfix calculator engine."""
	opers = [
		{ # no operands
			"time": lambda: int(time.time()),
			"rand": lambda: random.random(),
			"e": lambda: math.e, "pi": lambda: math.pi, "i": lambda: 1j
		},
		{ # 1 operand
			"~": lambda x: ~x, "sqrt": cmath.sqrt, "ln": cmath.log, "log": cmath.log10,
			"sin": cmath.sin, "cos": cmath.cos, "tan": cmath.tan, "exp": cmath.exp,
			"asin": cmath.asin, "acos": cmath.acos, "atan": cmath.atan,
			"rad": math.radians, "deg": math.degrees, "floor": math.floor,
			"ceil": math.ceil, "abs": math.fabs, "!": math.factorial,
			"1/x": lambda x: 1/x, "inv": lambda x: 1/x,
			">C": lambda x: (x - 32) * 5/9, ">F": lambda x: 9/5 * x + 32,
			">K": lambda x: x + 273.15, "<K": lambda x: x - 273.15,
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
		"d": lambda self: self.diceroll(),
		"(": lambda self: self.begstack(),
		")": lambda self: self.endstack(),
	}
	bases = {"b": 2, "o": 8, "h": 16, "x": 16}

	def __init__(self):
		self.stack = []
		self.stackstack = []

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
	def diceroll(self):
		b, a = self.stack.pop(), self.stack.pop()
		self.stack.extend([random.randint(1, b) for i in range(a)])

	def begstack(self):
		self.stackstack.append(self.stack)
		self.stack = []
	def endstack(self):
		if len(self.stackstack) == 0:
			raise StackUnderflow
		self.stack.extend(self.stackstack.pop())

	def calc(self, expr):
		self.stack = []
		self.stackstack = []
		for token in expr.split():
			if token in self.opers[0]:
				self.stack.append(self.opers[0][token]())
			elif token in self.opers[1]:
				if len(self.stack) == 0:
					self.stack = None
					raise StackUnderflow
				self.stack.append(self.opers[1][token](self.stack.pop()))
			elif token in self.opers[2]:
				if len(self.stack) < 2:
					self.stack = None
					raise StackUnderflow
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
		self.stack = [int(i) if not isinstance(i, complex) and \
			float(i).is_integer() else i for i in self.stack]

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

	strfuncs = {
		2: lambda x: bin(x)[2:] + "b",
		8: lambda x: oct(x)[2:] + "o",
		10: str,
		16: lambda x: hex(x)[2:].upper() + "h"
	}

	def ensure_context(self, chan):
		if chan not in self.contexts:
			self.contexts[chan] = Calculator()

	def _calc(self, to, expr):
		self.ensure_context(to)
		try:
			self.contexts[to].calc(expr)
		except ZeroDivisionError:
			self.circa.say(to, "\x0304\x02Error\x02\x03: Division by zero")
			return []
		except StackUnderflow:
			self.circa.say(to, "\x0304\x02Error\x02\x03: Stack underflow")
		return self.contexts[to].stack or []

	def str(self, num, base=10):
		if base not in self.strfuncs:
			return
		if isinstance(num, int):
			return self.strfuncs[base](num)
		elif isinstance(num, float):
			if num.is_integer():
				return self.str(int(num), base)
			if base != 10:
				# TODO: base conversion
				return "<fraction>"
			return str(num)
		elif isinstance(num, complex):
			if base != 10:
				# TODO: base conversion
				return "<complex>"
			re, im = num.real, num.imag
			if im == 0:
				return self.str(re, base)
			return (self.str(re, base) + "+" if re else "") + \
				("" if im == 1 else self.str(im, base)) + "i"
		else:
			return str(num)

	def calc(self, fr, to, expr, m):
		results = map(self.str, self._calc(to, expr))
		if results:
			self.circa.say(to, fr + ": " + ", ".join(results))

	def bcalc(self, fr, to, expr, m):
		results = map(lambda x: self.str(x, 2), self._calc(to, expr))
		if results:
			self.circa.say(to, fr + ": " + ", ".join(results))

	def ocalc(self, fr, to, expr, m):
		results = map(lambda x: self.str(x, 8), self._calc(to, expr))
		if results:
			self.circa.say(to, fr + ": " + ", ".join(results))

	def hcalc(self, fr, to, expr, m):
		results = map(lambda x: self.str(x, 16), self._calc(to, expr))
		if results:
			self.circa.say(to, fr + ": " + ", ".join(results))

module = CalcModule
