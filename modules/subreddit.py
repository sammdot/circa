import http.client as client
import re

class SubredditModule:
	subre = re.compile(r"^(?:.* )?/r/([A-Za-z0-9][A-Za-z0-9_]{2,20})")

	def __init__(self, circa):
		self.circa = circa
		self.events = {
			"message": [self.findsub]
		}

	def findsub(self, fr, to, msg, m):
		for sub in self.subre.findall(msg):
			print(sub)
			self.circa.say(to, "http://www.reddit.com/r/" + sub)

module = SubredditModule
