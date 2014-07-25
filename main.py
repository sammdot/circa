#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Usage: circa [options] CONFIG

Options:
    -s HOST  --server HOST      Connect to HOST
    -p PORT  --port PORT        Connect to port PORT [default: 6667]
    -P       --password         Provide a password prompt
    -n NICK  --nick NICK        Set nick [default: circa]
    -r NAME  --realname NAME    Set real name (ircname) to NAME [default: circa]
    -l FILE  --log FILE         Log to a file [default: circa.log]
    -c CHAR  --cmd CHAR         Set the prefix for command characters [default: \\]

    -v       --verbose          Log messages more verbosely
    -h       --help             Show this help message.
             --version          Display version information and quit.
"""

__version__ = 1.0

import docopt
import sys

def main():
	args = docopt.docopt(__doc__, version=__version__)

if __name__ == "__main__":
	main()
