
try:
    import _overlapped
except ImportError:
    from trollius import _overlapped


class CompletionPort(object):
    """
    An IOCP CompletionPort thing.
    """
