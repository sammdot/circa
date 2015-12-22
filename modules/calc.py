import cmath
import functools
import math
import operator
import random
import re
import time
import multiprocessing

class StackUnderflow(Exception):
	pass

class TimeLimitExceeded(Exception):
	pass

def floor(n):
	return math.floor(n.real) + math.floor(n.imag) if isinstance(n, complex) \
		else math.floor(n)
def ceil(n):
	return math.ceil(n.real) + math.ceil(n.imag) if isinstance(n, complex) \
		else math.ceil(n)

def simplify(n):
	if isinstance(n, complex):
		return n
	try:
		if float(n).is_integer():
			return int(n)
	except OverflowError:
		return float('inf')
	return n

class Calculator:
	"""A postfix calculator engine."""
	opers = [
		{ # no operands
			"time": lambda: int(time.time()),
			"rand": random.random,
			"e": lambda: math.e, "pi": lambda: math.pi, "i": lambda: 1j,
			"c": lambda: 299792458, "g": 9.80665,
			"-i": lambda: -1j
		},
		{ # 1 operand
			"~": lambda x: ~x, "sqrt": cmath.sqrt, "ln": cmath.log, "log": cmath.log10,
			"sin": cmath.sin, "cos": cmath.cos, "tan": cmath.tan, "exp": cmath.exp,
			"asin": cmath.asin, "acos": cmath.acos, "atan": cmath.atan,
			">R": math.radians, ">D": math.degrees, "abs": math.fabs,
			"!": math.factorial, "floor": floor, "ceil": ceil,
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
		"dup": lambda self: self.dup(),
		"swap": lambda self: self.swap(),
		"max": lambda self: self.max(),
		"min": lambda self: self.min(),
		"@>": lambda self: self.sort(),
		"@<": lambda self: self.sort(True),
		"@+": lambda self: self.sum(),
		"@*": lambda self: self.product(),
		"@^": lambda self: self.average(),
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
	def swap(self):
		self.stack[-1], self.stack[-2] = self.stack[-2], self.stack[-1]
	def max(self):
		self.stack = [max(self.stack)]
	def min(self):
		self.stack = [min(self.stack)]
	def sort(self, rev=False):
		self.stack = sorted(self.stack, reverse=rev)
	def sum(self):
		self.stack = [sum(self.stack)]
	def product(self):
		self.stack = [functools.reduce(operator.mul, self.stack, 1)]
	def average(self):
		self.stack = [sum(self.stack) / len(self.stack)]
	def range(self):
		to, fr = self.stack.pop(), self.stack.pop()
		self.stack.extend(range(fr, to + 1) if to > fr else range(to, fr + 1)[::-1])
	def diceroll(self):
		b, a = self.stack.pop(), self.stack.pop()
		self.stack.extend([random.randint(1, b) for i in range(a)])

	def begstack(self):
		self.stackstack.append(self.stack[:])
	def endstack(self):
		if len(self.stackstack) == 0:
			raise StackUnderflow
		self.stack = self.stackstack.pop() + self.stack.pop()

	def calc(self, expr, queue):
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
			elif token.startswith("/"):
				# subnet mask
				num = token[1:]
				try:
					self.stack.append(4294967295 ^ \
						sum([2 ** i for i in range(32 - int(num))]))
				except ValueError:
					pass
			elif token.count(".") == 3:
				# IP address
				nums = token.split(".")
				try:
					nums = list(map(int, nums))
					shift = lambda x: x[0] << x[1]
					self.stack.append(sum(map(shift, zip(nums, [24, 16, 8, 0]))))
				except ValueError:
					pass
			elif "/" in token and not token.endswith("/"):
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
		queue.put([simplify(i) for i in self.stack])

class CalcModule:
	require = "cmd"

	def __init__(self, circa):
		self.circa = circa
		self.contexts = {}
		self.queue = multiprocessing.Queue()

		self.events = {
			"cmd.calc": [self.calc],
			"cmd.bcalc": [self.bcalc],
			"cmd.ocalc": [self.ocalc],
			"cmd.hcalc": [self.hcalc],
			"cmd.ipcalc": [self.ipcalc],
		}
		self.docs = {
			"calc": "calc [expr] → evaluate the postfix expression. More info in the online docs.",
			"bcalc": "bcalc [expr] → like calc, but returns answers in binary",
			"ocalc": "ocalc [expr] → like calc, but returns answers in octal",
			"hcalc": "hcalc [expr] → like calc, but returns answers in hexadecimal",
			"ipcalc": "ipcalc [expr] → like calc, but returns answers as IPv4 addresses",
		}

	strfuncs = {
		2: lambda x: "0b" + bin(x)[2:],
		8: lambda x: "0o" + oct(x)[2:],
		10: str,
		16: lambda x: "0x" + hex(x)[2:].upper()
	}

	def ensure_context(self, chan):
		if chan not in self.contexts:
			self.contexts[chan] = Calculator()

	def _calc(self, to, expr):
		self.ensure_context(to)
		try:
			proc = multiprocessing.Process(target=self.contexts[to].calc, args=(expr, self.queue))
			proc.start()
			proc.join(2)
			if proc.is_alive():
				proc.terminate()
				raise TimeLimitExceeded
		except ZeroDivisionError:
			self.circa.say(to, "\x0304\x02Error\x02\x03: Division by zero")
			return []
		except StackUnderflow:
			self.circa.say(to, "\x0304\x02Error\x02\x03: Stack underflow")
			return []
		except TimeLimitExceeded:
			self.circa.say(to, "\x0304\x02Error\x02\x03: Time limit exceeded")
		return self.queue.get()

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
			return (self.str(re, base) + ("+" if im > 0 else "") if re else "") + \
				("-" if im < 0 else "") + ("" if abs(im) == 1 else \
				self.str(abs(im), base)) + "i"
		else:
			return str(num)

	def calc(self, fr, to, expr, m):
		results = list(map(self.str, self._calc(to, expr)))
		if results:
			self.circa.say(to, fr + ": " + ", ".join(results))

	def bcalc(self, fr, to, expr, m):
		results = list(map(lambda x: self.str(x, 2), self._calc(to, expr)))
		if results:
			self.circa.say(to, fr + ": " + ", ".join(results))

	def ocalc(self, fr, to, expr, m):
		results = list(map(lambda x: self.str(x, 8), self._calc(to, expr)))
		if results:
			self.circa.say(to, fr + ": " + ", ".join(results))

	def hcalc(self, fr, to, expr, m):
		results = list(map(lambda x: self.str(x, 16), self._calc(to, expr)))
		if results:
			self.circa.say(to, fr + ": " + ", ".join(results))

	def ipcalc(self, fr, to, expr, m):
		def ipify(num):
			if not isinstance(num, int):
				return "NaN.NaN.NaN.NaN"
			octets = [num >> 24 & 0xFF, num >> 16 & 0xFF, num >> 8 & 0xFF, num & 0xFF]
			return ".".join(map(str, octets))
		results = list(map(ipify, self._calc(to, expr)))
		if results:
			self.circa.say(to, fr + ": " + ", ".join(results))

module = CalcModule
