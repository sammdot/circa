import logging
import client

class Circa(client.Client):
	def __init__(self, conf):
		conf["autoconn"] = False

		for setting in "server nick username realname".split():
			if setting not in conf or conf[setting] is None:
				logging.error("Required setting %s not present", setting)
				logging.info("See %s for details", conf["log"])
				exit(1)

		client.Client.__init__(self, **conf)

		logging.info("Registering callbacks")
		self.add_listener("registered", self.registered)
		self.add_listener("invite", self.join)

	def registered(self, nick):
		self.send("UMODE2", "+B")
		if "password" in self.conf:
			self.send("PRIVMSG", "NickServ", "IDENTIFY {0}".format(
					str(self.conf["password"])))
		for chan in self.conf["channels"]:
			self.join("#" + chan)

	def close(self):
		self.send("QUIT")
		self.sock.close()
		self.sock = None
