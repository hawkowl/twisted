
try:
    import _overlapped
except ImportError:
    from trollius import _overlapped

from twisted.internet.iocpreactor import const


class CompletionPort(object):
    """
    An IOCP CompletionPort thing.
    """

    def __init__(self):

        self.port = _overlapped.CreateIoCompletionPort(
            _overlapped.INVALID_HANDLE_VALUE, 0, 0, 0)


    def getEvent(self, timeout):

        status = _overlapped.GetQueuedCompletionStatus(self.port, timeout)

        if status is None:
            # Trollius returns None, but the IOCP reactor wants something in
            # the same struct.
            return (const.WAIT_TIMEOUT, None, None, None)

        return status
