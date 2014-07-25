import logging
import client

class Circa(client.Client):
	def __init__(self, conf):
		conf["autoconn"] = False
		logging.basicConfig(filename=conf.get("log", "circa.log"), level=logging.INFO,
			style="%", format="%(asctime)s %(levelname)s %(message)s")
		if "log" in conf:
			logging.basicConfig(filename=conf["log"])
		client.Client.__init__(self, **conf)
