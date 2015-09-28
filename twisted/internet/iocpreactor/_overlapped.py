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

typedef struct _OVERLAPPED { ...; } OVERLAPPED;
typedef struct sockaddr { ...; };
typedef struct sockaddr_in { ...; short   sin_family; };
typedef struct sockaddr_in6 { ...; };

int initWS();

static int initialize_function_pointers(void);

BOOL AcceptEx(HANDLE, HANDLE, char*, DWORD, DWORD, DWORD, LPDWORD, OVERLAPPED*);

BOOL CreateIoCompletionPort(HANDLE* fileHandle, HANDLE existing, ULONG_PTR key, DWORD numThreads);
BOOL GetQueuedCompletionStatus(HANDLE port, DWORD *bytes, ULONG_PTR *key, OVERLAPPED **ov, DWORD timeout);
BOOL PostQueuedCompletionStatus(HANDLE port, DWORD bytes, ULONG_PTR key, OVERLAPPED *ov);


BOOL Py_ConnectEx(HANDLE, const sockaddr, int, PVOID, DWORD, LPDWORD, OVERLAPPED*);
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

int initWS()
{
    WSADATA wsa;

    if (WSAStartup(MAKEWORD(2,2),&wsa) != 0)
    {
        return 1;
    }
    
    return 0;
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
    HINSTANCE hKernel32;
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

""")

ffi.compile()


from _overlapped2 import ffi, lib

lib.initWS()
lib.initialize_function_pointers()

def parse_address(socket, address):

    if socket.family == AF_INET:

        addr = ffi.new("struct sockaddr_in*")

        addr.sin_family = AF_INET


    print(addr)

    return addr

def GetQueuedCompletionStatus(port, timeout):

    o = Overlapped(0)

    key = ffi.new("ULONG_PTR*")
    b = ffi.new("DWORD*")

    res = lib.GetQueuedCompletionStatus(port, b, key, o._ov, 0)

    if not res:
        return None


    return (wait[0], None, None, o)

def CreateIoCompletionPort(handle, port, key, concurrency):
    """
    returns a port
    """

    if not handle:
        h = ffi.new("HANDLE*")
    if isinstance(handle, int):
        h = ffi.new("HANDLE*", handle)
        print(port)
        print(h)

    a = lib.CreateIoCompletionPort(h, port, 0, 0)

    return h[0]

def PostQueuedCompletionStatus(port, bytes, key, whatever):

    o = Overlapped(0)

    a = lib.PostQueuedCompletionStatus(port, bytes, key, o._ov[0])
    return a


class Overlapped(object):

    def __init__(self, handle):
        assert handle == 0

        self._ov = ffi.new("OVERLAPPED**")

    @property
    def address(self):
        return self._ov
    

    def AcceptEx(self, listen, accept):

        size = (ffi.sizeof("struct sockaddr_in6") + 16) * 2

        buf = ffi.new("char[" + str(size) + "]")

        recv = ffi.new("unsigned long*")
        recvDesired = 0
        sizeOf = size


        res = lib.AcceptEx(
            listen.fileno(), accept.fileno(),
            ffi.addressof(buf),
            0, size, size, recv, self._ov[0]
            )   

        return res

    def ConnectEx(self, socket, address):

        addr = parse_address(socket, address)

        length = ffi.sizeof(addr)

        res = lib.Py_ConnectEx(

            socket.fileno(),
            addr[0],
            length,
            0, 0, 0, self._ov[0]

        )   

        return res
