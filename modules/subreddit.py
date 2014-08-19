import re
import urllib.request as req
import urllib.error   as err

class SubredditModule:
	subre = re.compile(r"^(?:.* )?/r/([A-Za-z0-9][A-Za-z0-9_]{2,20})")

	def __init__(self, circa):
		self.circa = circa
		self.events = {
			"message": [self.findsub]
		}

	def findsub(self, fr, to, msg, m):
		for sub in self.subre.findall(msg):
			try:
				r = req.Request("http://api.reddit.com/r/" + sub + ".json")
				r.get_method = lambda: "HEAD"
				req.urlopen(r)
				self.circa.say(to, "http://www.reddit.com/r/" + sub)
			except err.HTTPError as e:
				pass

module = SubredditModule
