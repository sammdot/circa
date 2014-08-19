import re
import urllib.request as req

class SubredditModule:
	subre = re.compile(r"^(?:.* )?/r/([A-Za-z0-9][A-Za-z0-9_]{2,20})")

	def __init__(self, circa):
		self.circa = circa
		self.events = {
			"message": [self.findsub]
		}

	def findsub(self, fr, to, msg, m):
		for sub in self.subre.findall(msg):
			url = "http://www.reddit.com/r/" + sub
			try:
				req.urlopen(url)
				self.circa.say(to, url)
			except:
				pass

module = SubredditModule
