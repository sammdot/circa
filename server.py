class Server:
	def __init__(self, host, port):
		self.host = host
		self.port = port

		self.motd = ""

		self.usermods = set()
		self.kicklength = 0
		self.maxlist = {}
		self.maxtargets = {}
		self.modes = 3
		self.nicklength = 9
		self.topiclength = 0

		self.idlength = {}
		self.chlength = 200
		self.chlimit = {}
		self.chmodes = {x: set() for x in "abcd"}
		self.types = set()

		self.prefix_mode = {}
		self.mode_prefix = {}
