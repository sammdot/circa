# Circa

Circa is a modular asynchronous Python IRC bot. It was written from the bottom up
using a simple event-based multithreaded IRC client framework.

This program requires Python 3.4 or newer. The core depends on only the Python
standard library, but certain modules may require certain other features being
available. (For example, the `shell` module that comes with circa requires a `bash`
shell to be present, but this can be changed if necessary.)

## Getting Started

### Configure

Circa can be configured using a `.cfg` file in INI format. This repository contains
a sample configuration file `sample.cfg`. Simply edit the details to fit your server
configuration and add the channels and modules as necessary.

* `[server]` contains details on how to connect to the server.

* `[channels]` specifies what channels the bot joins once it is connected.

* `[modules]` specifies what modules to load at startup.

* `[admins]` is a list of nick!user@host masks that match the bot's admins.

* `[bot]` contains the options for command prefix and log file. 

### Run

Run the script `circa`, specifying the name of the config file as an argument.
See `circa --help` to provide additional options, which will override those
in the config file.

