import logging
import client

class Circa(client.Client):
	def __init__(self, conf):
		conf["autoconn"] = False
		logging.basicConfig(filename=conf.get("log", "circa.log"), level=logging.INFO,
			style="%", format="%(asctime)s %(levelname)s %(message)s")

		for setting in "server nick username realname".split():
			if setting not in conf:
				logging.error("Required setting %s not present", setting)
				logging.info("See %s for details", conf.get("log", "circa.log"))
				exit(1)

		client.Client.__init__(self, **conf)
