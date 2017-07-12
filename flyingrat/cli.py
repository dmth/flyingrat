# -*- coding: utf-8 -*-
from __future__ import (unicode_literals, print_function, division,
                        absolute_import)

import os
import asyncore
from smtpd import SMTPServer
import tempfile

import argparse

from flyingrat.store.store import Store
from flyingrat.pop3.pop3 import Server as Pop3Server


def parse_address(address):
    parts = address.split(':')
    return ':'.join(parts[:-1]), int(parts[-1])


def validate_address(value):
    try:
        return parse_address(value)
    except ValueError:
        raise argparse.ArgumentTypeError('Address needs to be in format host:port')

def cli(mode, smtp_address, pop3_address, pop3_user, pop3_password, directory):
    """
    Runs an SMTP server, POP3 server or both based on a directory.

    When no directory is supplied, a temporary directory will be created and
    used. The POP3 server accepts any username and password combination by
    default.

    """

    if directory is None:
        directory = tempfile.mkdtemp()
    else:
        if not os.path.exists(directory):
            os.makedirs(directory)

    print('Running from directory %s' % directory)

    store = Store(directory)
    store.load()

    if mode in ('smtp', 'both'):
        print("SMTP on address %s : %s" % (smtp_address[0], smtp_address[1]))
        Smtp(smtp_address, None, store=store)
    if mode in ('pop3', 'both'):
        print("POP3 on address %s : %s" % (pop3_address[0], pop3_address[1]))
        Pop3Server(pop3_address, store, pop3_user, pop3_password)
    try:
        asyncore.loop()
    except KeyboardInterrupt:
        pass


class Smtp(SMTPServer):

    def __init__(self, *args, **kwargs):
        self.store = kwargs.pop('store')
        SMTPServer.__init__(self, *args, **kwargs)

    def process_message(self, peer, mailfrom, rcpttos, data):
        self.store.save(data)


def main():
    parser = argparse.ArgumentParser(description='Create a POP3/SMTP server and serve contents of a local .mbox file')

    from . import __version__
    parser.add_argument('--version', action='version', version=('Version %s' % __version__))

    parser.add_argument('-m',
                        '--mode',
                        choices=['smtp', 'pop3', 'both'],
                        default='both',
                        help='Run smtp, pop3 or both (default)',
                        nargs='?')
    parser.add_argument('-sa',
                        '--smtp-address',
                        default='localhost:5050',
                        help='Address to run the SMTP server on. Defaults to localhost:5050',
                        type=validate_address,
                        nargs='?')
    parser.add_argument('-pa',
                        '--pop3-address',
                        default='localhost:5051',
                        help='Address to run the POP3 server on. Defaults to localhost:5051',
                        type=validate_address,
                        nargs = '?')
    parser.add_argument('-pu',
                        '--pop3-user',
                        default=None,
                        help='Username for the POP3 server (default: <any>)',
                        nargs='?')
    parser.add_argument('-pp',
                        '--pop3-password',
                        default=None,
                        help='Password for the POP3 server (default: <any>)',
                        nargs='?')

    parser.add_argument('directory',
                        type=str,
                        help="The directory where the .mbox files are",
                        nargs='?')

    args = parser.parse_args()


    cli(mode = args.mode,
        smtp_address = args.smtp_address,
        pop3_address = args.pop3_address,
        pop3_user=args.pop3_user,
        pop3_password=args.pop3_password,
        directory = args.directory)

if __name__ == "__main__":
    main()
