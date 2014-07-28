import re
import subprocess

class CalcModule:
	def __init__(self, circa):
		self.circa = circa
		self.contexts = {}

	def onload(self):
		self.circa.add_listener("cmd.dc", self.dc)
		self.circa.add_listener("cmd.dc!", self.dc1)
		self.circa.add_listener("cmd.bc", self.bc)

	def onunload(self):
		self.circa.remove_listener("cmd.dc", self.dc)
		self.circa.remove_listener("cmd.dc!", self.dc1)
		self.circa.remove_listener("cmd.bc", self.bc)
	
	def dc(self, fr, to, expr):
		expr = re.sub(r"-([0-9])", r"_\1", expr)
		self.dc1(fr, to, expr + " p")

	def dc1(self, fr, to, expr):
		if to not in self.contexts:
			self.contexts[to] = None
		expr = re.sub(r"\b_\b", str(self.contexts[to]), expr)
		expr += "q\n"
		self.contexts[to] = str(subprocess.check_output(["dc", "-"],
			input=bytes(expr, "utf-8"), stderr=subprocess.STDOUT), "utf-8")
		self.circa.say(to, str(self.contexts[to]))

	def bc(self, fr, to, expr):
		if to not in self.contexts:
			self.contexts[to] = None
		expr = re.sub(r"\b_\b", str(self.contexts[to]), expr) + ";\n"
		self.contexts[to] = str(subprocess.check_output(["bc", "-l"],
			input=bytes(expr, "utf-8"), stderr=subprocess.STDOUT), "utf-8")
		self.circa.say(to, str(self.contexts[to]))

module = CalcModule
