
from . import _overlapped

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

    def __repr__(self):
        return "<event cb={} owner={}>".format(self.callback, self.owner)


class CompletionPort(object):
    """
    An IOCP CompletionPort thing.
    """

    def __init__(self, reactor):

        self.reactor = reactor
        self.events = {}
        self.ports = []

        self.port = _overlapped.CreateIoCompletionPort(
            None, 0, 0, 0)


    def getEvent(self, timeout):
        status = _overlapped.GetQueuedCompletionStatus(self.port, timeout)
        status = list(status)

        if status[0] != 0:
            print("TICK", status)
            print("TICK", [(key, val.callback) for key,val in self.events.items()])

        if status[3] in self.events.keys():
            status[3] = self.events.pop(status[3])

        return status

    def postEvent(self, b, key, event):
        _overlapped.PostQueuedCompletionStatus(self.port, b, key, 0)

    def addHandle(self, handle, key):
        _overlapped.CreateIoCompletionPort(handle, self.port, key, 0)


def accept(listening, accepting, event):

    ov = _overlapped.Overlapped(0)
    res = ov.AcceptEx(listening, accepting)

    event.overlapped = ov
    event.owner.reactor.port.events[ov.address] = event
    event.port = ov

    return res


def connect(socket, address, event):

    ov = _overlapped.Overlapped(0)
    res = ov.ConnectEx(socket, address)

    event.overlapped = ov
    event.owner.reactor.port.events[ov.address] = event

    return res


def recv(socketFn, len, event, flags=0):

    ov = _overlapped.Overlapped(0)
    event.overlapped = ov
    event.owner.reactor.port.events[ov.address] = event

    try:
        res = ov.WSARecv(socketFn, len, flags)
    except OSError as e:
        res = e.winerror

    return res


def recvfrom(socketFn, len, event, flags=0):

    ov = _overlapped.Overlapped(0)
    event.overlapped = ov
    event.owner.reactor.port.events[ov.address] = (event, ov)

    try:
        res = ov.WSARecv(socketFn, len, flags)
    except OSError as e:
        res = e.winerror

    return res


def send(socketFn, data, event, flags=0):

    ov = _overlapped.Overlapped(0)
    event.overlapped = ov
    event.owner.reactor.port.events[ov.address] = (event, ov)

    try:
        res = ov.WSASend(socketFn, data, flags)
    except OSError as e:
        res = e.winerror

    return res
