# -*- coding: utf-8 -*-
from __future__ import (unicode_literals, print_function, division,
                        absolute_import)

import os
import errno
import mailbox
import contextlib
import io
import datetime
import uuid


class Message(object):

    def __init__(self, message, counter):
        self.message = message
        self.nr = counter
        self.uid = uuid.uuid4().hex
        self.path = io.BytesIO(message.as_string())
        self.size = len(message.as_string()) # Not sure if this is equal to the size in bytes
        self.deleted = True if 'D' in message.get_flags() else False


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
        self.counter = 0
        self.messages = []
        self.inbox = _create_inbox(directory)
        self.outbox = _create_outbox(directory)

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
        self.counter = len(self.inbox.values())

        for key, value in self.inbox.items():
            self.messages.append(Message(value, key))

        if self.counter == 0:
            print("The inbox file seems to be empty.")

        self.inbox.unlock()

    def get(self, nr, include_deleted=False):
        print("Getting Message with key %s"% (nr))
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
        print("Saving Message to Outbox")
        with self.outbox as mbox:
            mbox.add(mailbox.mboxMessage(data))

    def delete_marked_messages(self):
        print("Was asked to delete Messages.")
        print("Deleting Messages is not supported, yet")
        for m in self.messages:
            if m.deleted:
                print("Deleting Message with Key: %s"% (m.nr))
                self.inbox.remove(m.nr)
                self.messages.remove(m)
        return True

