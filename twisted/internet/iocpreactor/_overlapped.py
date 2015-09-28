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

typedef struct _OVERLAPPED {
#ifdef WORDS_BIGENDIAN
        ULONG_PTR InternalHigh;
        ULONG_PTR Internal;
#else
        ULONG_PTR Internal;
        ULONG_PTR InternalHigh;
#endif
        union {
            struct {
#ifdef WORDS_BIGENDIAN
                DWORD OffsetHigh;
                DWORD Offset;
#else
                DWORD Offset;
                DWORD OffsetHigh;
#endif
            } DUMMYSTRUCTNAME;
            PVOID Pointer;
        } DUMMYUNIONNAME;
         HANDLE hEvent;
} OVERLAPPED, *LPOVERLAPPED;
""")

lib = ffi.dlopen(ctypes.util.find_library("c"))

def GetQueuedCompletionStatus(port, timeout):
    lib.GetQueuedCompletionStatus()
