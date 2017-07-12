Flying Rat
==========

Flying Rat is a simple mail server for local development. It supports both SMTP to send messages and POP3 to fetch them.

All messages over SMTP are dropped into an .mbox-file named after the current date, which allows you to test your application with real email addresses without running the risk of actually sending messages to those recipients.
Running a simple mail server also means it's a lot easier to configure your application to send those messages during local development.
The SMTP server runs on localhost at port 5050 by default and that's all you need to configure.

When a message is received it's stored on disk, either to a temporary directory or a directory of your choosing::

    flyingrat
    Running from directory /tmp/tmpV1mYQY
    SMTP on address localhost : 5050
    POP3 on address localhost : 5051

This means you can examine the contents of the directory to view the actual message.
But by default Flying Rat will also run a basic POP3 server on port 5051.
It serves the file ``inbox.mbox`` by pop3.


Installing
----------

You can install flyingrat using pip::

    pip2 install .


You may also run the script directly, for instance::

    python2 -m flyingrat.cli


Options
-------

The most reliable source for possible options is the application itself. Just pass in the ``--help`` option::

    flyingrat --help
    usage: flyingrat [-h] [--version] [-m [{smtp,pop3,both}]] [-sa [SMTP_ADDRESS]]
                    [-pa [POP3_ADDRESS]] [-pu [POP3_USER]] [-pp [POP3_PASSWORD]]
                    [directory]

    Create a POP3/SMTP server and serve contents of a local .mbox file

    positional arguments:
    directory             The directory where the .mbox files are

    optional arguments:
    -h, --help            show this help message and exit
    --version             show program's version number and exit
    -m [{smtp,pop3,both}], --mode [{smtp,pop3,both}]
                            Run smtp, pop3 or both (default)
    -sa [SMTP_ADDRESS], --smtp-address [SMTP_ADDRESS]
                            Address to run the SMTP server on. Defaults to
                            localhost:5050
    -pa [POP3_ADDRESS], --pop3-address [POP3_ADDRESS]
                            Address to run the POP3 server on. Defaults to
                            localhost:5051
    -pu [POP3_USER], --pop3-user [POP3_USER]
                            Username for the POP3 server (default: <any>)
    -pp [POP3_PASSWORD], --pop3-password [POP3_PASSWORD]
                            Password for the POP3 server (default: <any>)

