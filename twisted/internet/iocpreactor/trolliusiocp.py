
try:
    import _overlapped
except ImportError:
    from trollius import _overlapped


class CompletionPort(object):
    """
    An IOCP CompletionPort thing.
    """

    def __init__(self):

        self.port = _overlapped.CreateIoCompletionPort(
            _overlapped.INVALID_HANDLE_VALUE, 0, 0, 0)


    def getEvent(self, timeout):

        status = _overlapped.GetQueuedCompletionStatus(self.port, timeout)

        if not status:
            status = (0, b"", 0, None)

        return status
