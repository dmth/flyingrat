# -*- coding: utf-8 -*-
from __future__ import (unicode_literals, print_function, division,
                        absolute_import)

import asyncore
import asynchat
import socket
import io


class Request(object):

    def __init__(self, command, *args):
        self.command = command
        self.args = args

    @property
    def arg(self):
        return None if not self.args else self.args[0]

    @property
    def message_nr(self):
        arg = self.arg
        return None if arg is None else int(arg)

    @property
    def has_args(self):
        return self.args is not None and len(self.args) > 0

    @property
    def merged_arg(self):
        if self.args is None:
            return None
        return ' '.join(self.args)


class Response(object):

    def __init__(self, status, lines=None):
        self.status = status
        self.lines = lines

    @classmethod
    def error(cls, lines=None):
        return cls(b'-ERR', lines)

    @classmethod
    def ok(cls, lines=None):
        return cls(b'+OK', lines)

    @classmethod
    def ok_extra(cls, msg, lines=None):
        return cls(b'+OK %s' % msg, lines)


class Pop3Exception(Exception):
    pass


def stream_to_lines(stream):
    """
    Should work on a io.BytesIO, or on an open file.
    Turns and email into lines suitable for POP§ transfer:
      * no line-endings
      * leading dot characters byte-stuffed

    :param stream: io.BytesIO or file
    :return: a generator that yields lines with type bytes (aka 'str')
    """
    with stream as f:
        last = None
        line = []
        while True:
            current = bytes(f.read(1))
            if current == b'':
                # EOF
                yield b''.join(line)
                return
            line.append(current)
            if len(line) == 1 and current == b'.':
                    # EOT indicator is .\r\n -- stuff extra dot at new line
                    line.append(b'.')
            if current == b'\n':
                # Done with this line
                if last == b'\r':
                    # pass it without \r\n
                    yield b''.join(line[:-2])
                else:
                    # pass it without \n
                    yield b''.join(line[:-1])
                line = []

            last = current


class Session(asynchat.async_chat):

    def __init__(self, sock, store, user, password):
        asynchat.async_chat.__init__(self, sock)
        self.store = store
        self.user = user
        self.password = password
        self.buffer = []
        self.set_terminator(b'\r\n')

    def collect_incoming_data(self, data):
        self.buffer.append(data)

    def clear_buffer(self):
        raw_request = b''.join(self.buffer).strip()
        self.buffer = []
        return raw_request

    def found_terminator(self):
        request_parts = self.clear_buffer().split()
        request = Request(request_parts[0], *request_parts[1:])
        handler = getattr(self, b'do_%s' % request.command.lower(), None)
        response = None
        if handler and callable(handler):
            try:
                response = handler(request)
            except Pop3Exception:
                response = Response.error()
        if not response:
            response = Response.error()
        self.respond(response)

    def do_noop(self, request):
        return Response.ok()

    def do_user(self, request):
        if not self.user:
            # Anything will do when no user was set
            return Response.ok()
        if self.user == request.merged_arg:
            return Response.ok()
        raise Pop3Exception()

    def do_pass(self, request):
        # TODO Begin transaction
        if not self.password:
            # Anything will do when no password was set
            return Response.ok()
        if self.password == request.merged_arg:
            return Response.ok()
        raise Pop3Exception()

    def do_quit(self, request):
        # TODO Commit transaction
        if self.store.delete_marked_messages():
            return Response.ok()
        raise Pop3Exception()

    def do_retr(self, request):
        m = self.store.get(request.message_nr)
        if not m:
            raise Pop3Exception()
        return Response.ok(stream_to_lines(m.path))

    def do_capa(self, request):
        capabilities = [n for n in dir(self)
                        if n.startswith(b'do_') and callable(getattr(self, n))]
        return Response.ok([n[3:].upper() for n in capabilities])

    def do_stat(self, request):
        msg = b'%d %d' % (len(self.store), self.store.total_byte_size)
        return Response.ok_extra(msg)

    def do_rset(self, request):
        m = self.store.get(request.message_nr, include_deleted=True)
        if m:
            m.deleted = False
            return Response.ok()
        raise Pop3Exception()

    def do_dele(self, request):
        m = self.store.get(request.message_nr)
        if m:
            m.deleted = True
            return Response.ok()
        raise Pop3Exception()

    def do_list(self, request):
        if not request.has_args:
            if len(self.store) > 0:
                return Response.ok([b'%d %d' % (m.nr, m.size) for m in self.store])
            else:
                return Response.ok_extra(b'Mailbox is empty')
        m = self.store.get(request.message_nr)
        if m:
            return Response.ok_extra(b'%d %d' % (m.nr, m.size))
        raise Pop3Exception()

    def do_uidl(self, request):
        if not request.has_args:
            if len(self.store) > 0:
                return Response.ok([b'%d %s' % (m.nr, m.uid) for m in self.store])
            else:
                return Response.ok_extra(b'Mailbox is empty')
        m = self.store.get(request.message_nr)
        if m:
            return Response.ok_extra('%d %s' % (m.nr, m.uid))
        raise Pop3Exception()

    def respond(self, response):
        self.push((b'%s\r\n' % response.status).encode('ascii'))
        if response.lines:
            for line in response.lines:
                msg = b'%s\r\n' % line
                self.push(msg)
            self.push(b'.\r\n'.encode('ascii'))


class Server(asyncore.dispatcher):

    def __init__(self, address, store, user, password):
        asyncore.dispatcher.__init__(self)
        self.store = store
        self.user = user
        self.password = password
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind(address)
        self.listen(5)

    def handle_accept(self):
        pair = self.accept()
        if pair is not None:
            # TODO Handle disconnect
            sock, addr = pair
            sock.send(b'+OK Welcome to Flying Rat\r\n')
            Session(sock, self.store, self.user, self.password)
