import ctypes

from socket import AF_INET, AF_INET6

from cffi import FFI
ffi = FFI()



ffi.cdef("""

typedef size_t HANDLE;
typedef size_t SOCKET;
typedef unsigned long DWORD;
typedef size_t ULONG_PTR;
typedef int BOOL;

typedef struct _IN_ADDR { ...; } IN_ADDR;

typedef struct _OVERLAPPED { ...; } OVERLAPPED;

typedef struct sockaddr {
    ...;
    short sa_family;
};

typedef struct sockaddr_in { ...;
    short sin_family;
    unsigned short sin_port;
    char sin_addr[4];
};
typedef struct sockaddr_in6 { ...; 
    short sin6_family;
    unsigned short sin6_port;
    char sin6_addr[16];
};


typedef struct __WSABUF {
    ULONG len;
    char *buf;
} WSABUF;

static int initialize_function_pointers(void);

BOOL AcceptEx(HANDLE, HANDLE, char*, DWORD, DWORD, DWORD, LPDWORD, OVERLAPPED*);

HANDLE CreateIoCompletionPort(HANDLE fileHandle, HANDLE existing, ULONG_PTR key, DWORD numThreads);
BOOL GetQueuedCompletionStatus(HANDLE port, DWORD *bytes, ULONG_PTR *key, intptr_t *overlapped, DWORD timeout);
BOOL PostQueuedCompletionStatus(HANDLE port, DWORD bytes, ULONG_PTR key, OVERLAPPED *ov);

BOOL Tw_ConnectEx4(HANDLE, struct sockaddr_in*, int, PVOID, DWORD, LPDWORD, OVERLAPPED*);
BOOL Tw_ConnectEx6(HANDLE, struct sockaddr_in6*, int, PVOID, DWORD, LPDWORD, OVERLAPPED*);

int WSARecv(HANDLE, struct __WSABUF* buffs, DWORD buffcount, DWORD *bytes, DWORD *flags, OVERLAPPED *ov, void *crud);
int WSARecvFrom(HANDLE s, WSABUF *buffs, DWORD buffcount, DWORD *bytes, DWORD *flags, struct sockaddr *fromaddr, int *fromlen, OVERLAPPED *ov, void *crud);

int WSASend(HANDLE s, WSABUF *buffs, DWORD buffcount, DWORD *bytes, DWORD flags, OVERLAPPED *ov, void *crud);

int WSAGetLastError(void);

HANDLE getInvalidHandle();
""")

ffi.set_source("_overlapped2",
"""
#include <sys/types.h>

#define WINDOWS_LEAN_AND_MEAN
#include <winsock2.h>
#include <ws2tcpip.h>
#include <mswsock.h>
#include <in6addr.h>


#pragma comment(lib, "Mswsock.lib")
#pragma comment(lib, "ws2_32.lib")

HANDLE getInvalidHandle() {
    return INVALID_HANDLE_VALUE;
}

static LPFN_ACCEPTEX Py_AcceptEx = NULL;
static LPFN_CONNECTEX Py_ConnectEx = NULL;
static LPFN_DISCONNECTEX Py_DisconnectEx = NULL;


#define GET_WSA_POINTER(s, x)                                           \
    (SOCKET_ERROR != WSAIoctl(s, SIO_GET_EXTENSION_FUNCTION_POINTER,    \
                              &Guid##x, sizeof(Guid##x), &Py_##x,       \
                              sizeof(Py_##x), &dwBytes, NULL, NULL))

static int
initialize_function_pointers(void)
{
    GUID GuidAcceptEx = WSAID_ACCEPTEX;
    GUID GuidConnectEx = WSAID_CONNECTEX;
    GUID GuidDisconnectEx = WSAID_DISCONNECTEX;
    SOCKET s;
    DWORD dwBytes;

    s = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);

    if (!GET_WSA_POINTER(s, AcceptEx) ||
        !GET_WSA_POINTER(s, ConnectEx) ||
        !GET_WSA_POINTER(s, DisconnectEx))
    {
        closesocket(s);
        return -1;
    }

    closesocket(s);

    return 0;
}

BOOL Tw_ConnectEx4(HANDLE a, struct sockaddr_in* b , int c, PVOID d, DWORD e, LPDWORD f, OVERLAPPED* g) {
    return Py_ConnectEx(a, b, c, d, e, f, g);
}

BOOL Tw_ConnectEx6(HANDLE a, struct sockaddr_in6* b , int c, PVOID d, DWORD e, LPDWORD f, OVERLAPPED* g) {
    return Py_ConnectEx(a, b, c, d, e, f, g);
}

""")

ffi.compile()

NULL = ffi.NULL

from _overlapped2 import ffi, lib

lib.initialize_function_pointers()

def parse_address(socket, address):

    from socket import inet_pton, htons

    if socket.family == AF_INET:

        addr = ffi.new("struct sockaddr_in*")
        addr[0].sin_family = AF_INET
        addr[0].sin_port = htons(address[1])
        addr[0].sin_addr = inet_pton(AF_INET, address[0])

    elif socket.family == AF_INET6:

        addr = ffi.new("struct sockaddr_in6*")
        addr[0].sin6_family = AF_INET6
        addr[0].sin6_port = htons(address[1])
        addr[0].sin6_addr = inet_pton(AF_INET6, address[0])

    return addr

def GetQueuedCompletionStatus(port, timeout):

    key = ffi.new("ULONG_PTR*")
    b = ffi.new("DWORD*")
    ov = ffi.new("intptr_t*")

    rc = lib.GetQueuedCompletionStatus(port, b, key, ov, timeout)

    if not rc:
        rc = ffi.getwinerror()[0]
    else:
        rc = 0

    rval = (rc, b[0], key[0], int(ov[0]))

    return rval

def CreateIoCompletionPort(handle, port, key, concurrency):
    """
    returns a port
    """
    if isinstance(handle, int):
        h = handle
    else:
        h = lib.getInvalidHandle()

    a = lib.CreateIoCompletionPort(h, port, key, concurrency)

    if not a:
        raise Exception(ffi.getwinerror())

    return a

def PostQueuedCompletionStatus(port, bytes, key, whatever):
    o = Overlapped(0)
    a = lib.PostQueuedCompletionStatus(port, bytes, key, o._ov)

    if not a:
        raise Exception(ffi.getwinerror())

    return a


class Overlapped(object):

    def __init__(self, handle):
        assert handle == 0
        self._ov = ffi.new("OVERLAPPED*")
        self._buffer = None
        self._wsabuf = None
        self._handle = None


    def getresult(self, wait=False):
        f = ffi.buffer(self._buffer)
        return f

    def getRecvAddress(self):

        print(self.recvAddress.sa_family)



    @property
    def address(self):

        addr = int(ffi.cast("intptr_t", self._ov))
        return addr


    def AcceptEx(self, listen, accept):

        self._handle = accept

        size = ffi.sizeof("struct sockaddr_in6") + 16

        buf = ffi.new("char* [" + str(size) + "]")
        recv = ffi.new("DWORD*")
        recvDesired = 0
        sizeOf = size

        res = lib.AcceptEx(
            listen.fileno(), accept.fileno(),
            buf,
            0, size, size, recv, self._ov
        )

        if not res:
            return ffi.getwinerror()[0]

        return res

    def ConnectEx(self, socket, address):

        self._handle = socket

        addr = parse_address(socket, address)
        length = ffi.sizeof(addr[0])

        if socket.family == AF_INET:
            func = lib.Tw_ConnectEx4
        elif socket.family == AF_INET6:
            func = lib.Tw_ConnectEx6

        res = func(
            socket.fileno(),
            addr,
            length,
            ffi.NULL, 0, ffi.NULL, self._ov
        )   

        if not res:
            return ffi.getwinerror()[0]

        return res

    def WSARecv(self, socket, length, flags=0):

        self._handle = socket

        wsabuf = ffi.new("WSABUF*")

        buff = ffi.new("char [" + str(length) + "]")

        wsabuf[0].len = length
        wsabuf[0].buf = ffi.addressof(buff)

        self._buffer = buff
        self._wsabuf = wsabuf

        read = ffi.new("DWORD*")
        
        _flags = ffi.new("DWORD*")
        _flags[0] = flags

        bufflen = ffi.new("DWORD*")
        bufflen[0] = 1

        res = lib.WSARecv(socket, wsabuf, 1, read, _flags, self._ov, NULL)

        return ffi.getwinerror()[0], read[0]

    def WSARecvFrom(self, socket, length, flags=0):
    
        # int WSARecvFrom(HANDLE s, WSABUF *buffs, DWORD buffcount,
        # DWORD *bytes, DWORD *flags, sockaddr *fromaddr, int *fromlen,
        # OVERLAPPED *ov, void *crud)

        self._handle = socket

        wsabuf = ffi.new("WSABUF*")

        buff = ffi.new("char [" + str(length) + "]")

        wsabuf[0].len = length
        wsabuf[0].buf = ffi.addressof(buff)

        self._buffer = buff
        self._wsabuf = wsabuf

        read = ffi.new("DWORD*")
        
        _flags = ffi.new("DWORD*")
        _flags[0] = flags

        bufflen = ffi.new("DWORD*")
        bufflen[0] = 1

        recvAddress = ffi.new("struct sockaddr*")
        self.recvAddress = recvAddress

        print(recvAddress)
        print(recvAddress[0])
        print(ffi.sizeof(recvAddress[0]))
        print(recvAddress.sa_family)

        recvAddressSize = ffi.new("int*", ffi.sizeof(recvAddress[0]))

        res = lib.WSARecvFrom(socket, wsabuf, 1, read, _flags, recvAddress,
            recvAddressSize, self._ov, NULL)

        return ffi.getwinerror()[0], read[0]


    def WSASend(self, socket, data, flags=0):

        self._handle = socket

        wsabuf = ffi.new("WSABUF*")

        buff = ffi.new("char [" + str(len(data)+1) + "]", data)

        wsabuf[0].len = len(data)
        wsabuf[0].buf = ffi.addressof(buff)

        self._buffer = buff
        self._wsabuf = wsabuf

        _flags = ffi.new("DWORD*")
        _flags[0] = flags

        bytesSent = ffi.new("DWORD*")

        res = lib.WSASend(socket, wsabuf, 1, bytesSent, flags, self._ov, NULL)

        return ffi.getwinerror()[0], bytesSent[0]
