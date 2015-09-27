
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
        self.events = {}
        self.ports = []

        self.port = _overlapped.CreateIoCompletionPort(
            _overlapped.INVALID_HANDLE_VALUE, 0, 0, 0)


    def getEvent(self, timeout):

        status = _overlapped.GetQueuedCompletionStatus(self.port, timeout)

        if status is None:
            # Trollius returns None, but the IOCP reactor wants something in
            # the same struct.
            return (const.WAIT_TIMEOUT, None, None, None)

        status = list(status)
        status[3] = self.events.pop(status[3])[0]

        return status

    def addHandle(self, handle, key):
        port = _overlapped.CreateIoCompletionPort(handle, self.port, key, 0)


def accept(listening, accepting, event):

    ov = _overlapped.Overlapped(0)
    event.overlapped = ov
    event.owner.reactor.port.events[ov.address] = (event, ov)
    event.port = ov

    res = ov.AcceptEx(listening.fileno(), accepting.fileno())

    return res


def connect(socket, address, event):

    ov = _overlapped.Overlapped(0)
    event.overlapped = ov
    event.owner.reactor.port.events[ov.address] = (event, ov)

    res = ov.ConnectEx(socket.fileno(), address)

    return res


def recv(socketFn, len, event, flags=0):

    ov = _overlapped.Overlapped(0)
    event.overlapped = ov
    event.owner.reactor.port.events[ov.address] = (event, ov)

    res = ov.WSARecv(socketFn, len, flags)

    return res

def send(socketFn, data, event, flags=0):

    ov = _overlapped.Overlapped(0)
    event.overlapped = ov
    event.owner.reactor.port.events[ov.address] = (event, ov)

    res = ov.WSASend(socketFn, data, flags)

    return res