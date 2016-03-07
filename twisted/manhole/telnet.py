# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Telnet-based shell.
"""

from __future__ import absolute_import, division

import copy
import sys

from twisted.protocols import telnet
from twisted.internet import protocol
from twisted.python import log, failure
from twisted.python.compat import unicode, _PY3

if _PY3:
    from io import StringIO
else:
    from StringIO import StringIO


class Shell(telnet.Telnet):
    """A Python command-line shell."""

    def connectionMade(self):
        telnet.Telnet.connectionMade(self)
        self.lineBuffer = []

    def loggedIn(self):
        self.transport.write(b">>> ")

    def checkUserAndPass(self, username, password):
        if _PY3:
            username = username.decode('ascii')
            password = password.decode('ascii')
        return ((self.factory.username == username) and (password == self.factory.password))

    def write(self, data):
        """Write some data to the transport.
        """
        if isinstance(data, unicode):
            data = data.encode('ascii')

        self.transport.write(data)

    def telnet_Command(self, cmd):
        if self.lineBuffer:
            if not cmd:
                cmd = b'\n'.join(self.lineBuffer) + b'\n\n\n'
                self.doCommand(cmd)
                self.lineBuffer = []
                return "Command"
            else:
                self.lineBuffer.append(cmd)
                self.transport.write(b"... ")
                return "Command"
        else:
            self.doCommand(cmd)
            return "Command"

    def doCommand(self, cmd):

        # TODO -- refactor this, Reality.author.Author, and the manhole shell
        #to use common functionality (perhaps a twisted.python.code module?)
        fn = '$telnet$'
        result = None
        try:
            out = sys.stdout
            sys.stdout = self
            try:
                code = compile(cmd, fn, 'eval')
                result = eval(code, self.factory.namespace)
            except Exception:
                try:
                    code = compile(cmd, fn, 'exec')
                    if _PY3:
                        exec(code, self.factory.namespace)
                    else:
                        exec(code in self.factory.namespace)
                except SyntaxError as e:
                    if not self.lineBuffer and str(e)[:14] == "unexpected EOF":
                        self.lineBuffer.append(cmd)
                        self.transport.write(b"... ")
                        return
                    else:
                        failure.Failure().printTraceback(file=self)
                        log.deferr()
                        self.write(b'\r\n>>> ')
                        return
                except:
                    f = StringIO()
                    failure.Failure().printTraceback(file=f)
                    self.write(f.getvalue().encode('ascii'))
                    log.deferr()
                    self.write(b'\r\n>>> ')
                    return
        finally:
            sys.stdout = out

        self.factory.namespace['_'] = result
        if result is not None:
            self.write(repr(result))
            self.write(b'\r\n')
        self.write(b">>> ")



class ShellFactory(protocol.Factory):
    username = "admin"
    password = "admin"
    protocol = Shell
    service = None

    def __init__(self):
        self.namespace = {
            'factory': self,
            'service': None,
            '_': None
        }

    def setService(self, service):
        self.namespace['service'] = self.service = service

    def __getstate__(self):
        """This returns the persistent state of this shell factory.
        """
        dict = self.__dict__
        ns = copy.copy(dict['namespace'])
        dict['namespace'] = ns
        if ns.has_key('__builtins__'):
            del ns['__builtins__']
        return dict
