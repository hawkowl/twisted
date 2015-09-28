from cffi import FFI
ffi = FFI()

ffi.set_source("_overlapped",

               """
#include <sys/types.h>
#define WINDOWS_LEAN_AND_MEAN
#include <winsock2.h>
#include <ws2tcpip.h>
#include <mswsock.h>


               """)

ffi.cdef("""
BOOL GetQueuedCompletionStatus(HANDLE, LPDWORD, PULONG_PTR, LPOVERLAPPED*, DWORD);
""")

lib = ffi.dlopen(ctypes.util.find_library("c"))

def GetQueuedCompletionStatus(port, timeout):
    lib.GetQueuedCompletionStatus()
