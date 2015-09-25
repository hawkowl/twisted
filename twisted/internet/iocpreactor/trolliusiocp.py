
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
        self.ports = {}

        self.port = _overlapped.CreateIoCompletionPort(
            _overlapped.INVALID_HANDLE_VALUE, 0, 0, 0)


    def getEvent(self, timeout):

        status = _overlapped.GetQueuedCompletionStatus(self.port, timeout)

        print("GET Queues", status)


        if status is None:
            # Trollius returns None, but the IOCP reactor wants something in
            # the same struct.
            return (const.WAIT_TIMEOUT, None, None, None)

        print(status)

        return status

    def addHandle(self, handle, key):
        port = _overlapped.CreateIoCompletionPort(handle, self.port, key, 0)


def accept(listening, accepting):

    ov = _overlapped.Overlapped(0)
    try:
        res = ov.AcceptEx(listening.fileno(), accepting.fileno())

    except Exception as e:
        print('exc', e)
        res = e.errno

    print("done", res)
    return res
