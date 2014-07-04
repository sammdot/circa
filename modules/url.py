import lxml.html
import re

class URLModule:
	# https://gist.github.com/uogbuji/705383
	url_regex = re.compile(r"""((?:[a-z][\w-]+:(?:/{1,3}|[a-z0-9%])|www\d{0,3}[.]|[a-z0-9.\-]+[.‌​][a-z]{2,4}/)(?:[^\s()<>]+|(?:(?:[^\s()<>]+|(?:(?:[^\s()<>]+)))*))+(?:(?:(?:[^\s()<>]+|(?:‌​(?:[^\s()<>]+)))*)|[^\s`!()[]{};:'".,<>?«»“”‘’]))""", re.DOTALL)

	def __init__(self, circa):
		self.circa = circa

		self.listeners = {
			"message": [self.url]
		}

	def url(self, fr, to, text, msg):
		matches = self.url_regex.findall(text)
		for url in matches:
			try:
				title = self.findtitle(url)
				self.circa.say(to, "URL: {0}".format(title))
			except:
				continue

	def findtitle(self, url):
		return lxml.html.parse(url).find(".//title").text

module = URLModule
