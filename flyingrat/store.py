# -*- coding: utf-8 -*-
from __future__ import (unicode_literals, print_function, division,
                        absolute_import)

import os
import errno
import uuid
import mailbox
import contextlib
import io
from datetime import datetime


class Message(object):

    def __init__(self, message, counter):
        self.message = message
        self.nr = counter
        self.uid = message.get('Message-Id')
        self.path = io.BytesIO(message.as_string())
        self.size = len(message.as_string()) # Not sure if this is equal to the size in bytes
        self.deleted = True if 'D' in message.get_flags() else False

    def to_string(self):
        return self.message

@contextlib.contextmanager
def _create_mbox(dirname):
    """
    Creates an mbox named __outmail_name in the folder
    dirname
    :param dirname: The name of the directory where the mailbox shall be storeds
    :return:
    """
    __outmail_name = "sent.mbox"
    mbox = mailbox.mbox(dirname + os.sep + __outmail_name)
    try:
        mbox.lock()
        yield mbox

    finally:
        mbox.unlock()

@contextlib.contextmanager
def _load_mbox(dirname):
    __inmail_name = "sent.mbox"
    mbox = mailbox.mbox(dirname + os.sep + __inmail_name)
    try:
        mbox.lock()
        yield mbox

    finally:
        mbox.unlock()

class Store(object):

    def __init__(self, directory):
        self.directory = directory
        self.counter = 0
        self.messages = []
        self.mbox = directory

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
        Load the mbox file into the messages array
        :return:
        """
        self.messages = []
        self.counter = 0
        with _load_mbox(self.directory) as mbox:
            for message in mbox:
                self.counter += 1
                self.messages.append(Message(message, self.counter))

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
        with _create_mbox(self.directory) as mbox:
            mbox.add(mailbox.mboxMessage(data))


    def parse_uid(self, filename):
        return b'-'.join(filename[0:-len('.eml')].split('-')[1:])


    def delete_marked_messages(self):
        for m in self.messages:
            if m.deleted:
                try:
                    os.unlink(m.path)
                except OSError as e:
                    if e.errno != errno.ENOENT:
                        raise
                self.messages.remove(m)
        return True

