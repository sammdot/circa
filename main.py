#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Usage: circa [options] [CONFIG]

Options:
    -s HOST  --server HOST      Connect to HOST
    -p PORT  --port PORT        Connect to port PORT [default: 6667]
    -P       --password         Provide a password prompt
    -n NICK  --nick NICK        Set nick [default: circa]
    -u UNAME  --username UNAME  Set username [default: circa]
    -r NAME  --realname NAME    Set real name (ircname) to NAME [default: circa]
    -l FILE  --log FILE         Log to a file [default: circa.log]
    -c CHAR  --cmd CHAR         Set the prefix for command characters [default: \\]

    -v       --verbose          Log messages more verbosely
    -h       --help             Show this help message.
             --version          Display version information and quit.
"""

__version__ = 1.0

import docopt
import getpass
import logging
import signal
import sys
import yaml

from circa import Circa

circa = None

def sig(*args):
	if circa:
		circa.close()
	logging.info("Exiting.")
	exit(0)

signal.signal(signal.SIGINT, sig)
signal.signal(signal.SIGTERM, sig)

def main():
	args = docopt.docopt(__doc__, version=__version__)

	conf = {
		"server": args["-s"],
		"port": int(args["-p"]),
		"nick": args["-n"],
		"username": args["-u"],
		"realname": args["-r"],
		"log": args["-l"],
		"prefix": args["-c"],
		"verbose": args["-v"],
		"autoconn": False
	}

	if args["CONFIG"]:
		with open(args["CONFIG"]) as f:
			conf.update(yaml.load(f))

	logging.basicConfig(filename=conf["log"],
		level=logging.DEBUG if conf["verbose"] else logging.INFO,
		style="%", format="%(asctime)s %(levelname)s %(message)s")

	if args["-P"] and "password" not in conf:
		conf["password"] = getpass.getpass()

	print(conf)

	c = Circa(conf)
	c.connect()

if __name__ == "__main__":
	main()
