import re
import subprocess

class CalcModule:
	def __init__(self, circa):
		self.circa = circa
		self.contexts = {}

	def onload(self):
		self.circa.add_listener("cmd.dc", self.dc)
		self.circa.add_listener("cmd.dc!", self.dc1)

	def onunload(self):
		self.circa.remove_listener("cmd.dc", self.dc)
		self.circa.remove_listener("cmd.dc!", self.dc1)
	
	def dc(self, to, expr):
		self.dc1(to, expr + " p")

	def dc1(self, to, expr):
		if to not in self.contexts:
			self.contexts[to] = None
		expr = re.sub(r"-([0-9])", r"_\1", expr)
		expr = re.sub(r"\b_\b", str(self.contexts[to]), expr)
		expr += "q\n"
		self.contexts[to] = str(subprocess.check_output(["dc", "-"],
			input=bytes(expr, "utf-8"), stderr=subprocess.STDOUT), "utf-8")
		self.circa.say(to, str(self.contexts[to]))

module = CalcModule
