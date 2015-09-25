
try:
    import _overlapped
except ImportError:
    from trollius import _overlapped

import socket
import struct

from twisted.internet.iocpreactor import const
from twisted.internet.defer import Deferred


class Event(object):
    def __init__(self, callback, owner, **kw):
        self.callback = callback
        self.owner = owner
        for k, v in kw.items():
            setattr(self, k, v)


class CompletionPort(object):
    """
    An IOCP CompletionPort thing.
    """


    def __init__(self, reactor):

        self.reactor = reactor
        self.cache = {}

        self.port = _overlapped.CreateIoCompletionPort(
            _overlapped.INVALID_HANDLE_VALUE, 0, 0, 0)


    def getEvent(self, timeout):

        status = _overlapped.GetQueuedCompletionStatus(self.port, timeout)

        if status is None:
            # Trollius returns None, but the IOCP reactor wants something in
            # the same struct.
            return (const.WAIT_TIMEOUT, None, None, None)

    def addHandle(self, handle, key):
        _overlapped.CreateIoCompletionPort(handle, self.port, key, 0)


def accept(self, listening, accepting, event):

    ov = _overlapped.Overlapped(NULL)
    ov.AcceptEx(listening.fileno(), accepting.fileno())
