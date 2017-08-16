# -*- coding: utf-8 -*-
from __future__ import (unicode_literals, print_function, division,
                        absolute_import)

import contextlib
import datetime
from hashlib import sha256
import io
import mailbox
import os
import re


class Message(object):

    def __init__(self, message, key):
        self.message = message
        self.nr = key

        # we have to consider that
        # pop3.stream_to_lines() will remove line endings and
        # pop3.Session.respond() will later add '\r\n' to each line.
        # We simulate this behaviour here
        msg_as_string = re.sub(b'(?<=[^\r])\n',b'\r\n', message.as_string())
        self.uid = sha256(msg_as_string).hexdigest()
        self.size = len(msg_as_string)

        self.deleted = ('D' in self.message.get_flags())

    @property
    def path(self):
        return io.BytesIO(self.message.as_string())

@contextlib.contextmanager
def _create_outbox(dirname):
    """
    Creates the outgoing Mailbox, or provides access to it.
    :param dirname: the folder in which the .mbox file exists
    :return:
    """
    __outmail_name = str(datetime.date.today()) + '.mbox'
    mbox = mailbox.mbox(dirname + os.sep + __outmail_name)
    try:
        mbox.lock()
        yield mbox
    finally:
        mbox.unlock()


def _create_inbox(dirname):
    """
    Creates the incoming Mailbox, or provides access to it.
    :param dirname: the folder in which the .mbox file exists
    :return:
    """
    __inmail_name = "inbox.mbox"
    return mailbox.mbox(dirname + os.sep + __inmail_name)


class Store(object):

    def __init__(self, directory):
        self.directory = directory
        self.messages = []
        self.inbox = _create_inbox(directory)
        # self.outbox = _create_outbox(directory)

    def __len__(self):
        return len(self.non_deleted_messages)

    def __iter__(self):
        for m in self.non_deleted_messages:
            yield m

    @property
    def total_byte_size(self):
        return sum((m.size for m in self.non_deleted_messages))

    @property
    def non_deleted_messages(self):
        return [m for m in self.messages if not m.deleted]

    def load(self):
        """
        Load the inbox-mbox file into the flyingrat datastructure.
        :return:
        """
        self.inbox.lock()
        self.messages = []

        for key, value in self.inbox.items():
            # Start IDs with 1 and not with 0
            plussedkey = key+1
            self.messages.append(Message(value, plussedkey))

        self.inbox.unlock()

    def get(self, nr, include_deleted=False):
        messages = self.messages
        if not include_deleted:
            messages = self.non_deleted_messages
        for m in messages:
            if m.nr == nr:
                return m
        return None

    def save(self, data):
        """
        Saves a Message to the mbox
        :param data:
        :return:
        """
        with _create_outbox(self.directory) as mbox:
            mbox.add(mailbox.mboxMessage(data))

    def delete_marked_messages(self):
        self.inbox.lock()
        for m in self.messages:
            if m.deleted:
                # Remember we've +1ed the key in load()
                # so we need to -1 here
                self.inbox.remove(m.nr-1)
                self.messages.remove(m)
        self.inbox.flush()
        self.inbox.unlock()

        return True
