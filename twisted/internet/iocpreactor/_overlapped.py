from cffi import FFI
ffi = FFI()

ffi.set_source("_overlapped",

               """
#include <sys/types.h>

#define WINDOWS_LEAN_AND_MEAN
#include <basetsd.h>
#include <winsock2.h>
#include <ws2tcpip.h>
#include <mswsock.h>


               """)

ffi.cdef("""typedef struct _OVERLAPPED {
        ULONG_PTR Internal;
        ULONG_PTR InternalHigh;
        union {
            struct {
                DWORD Offset;
                DWORD OffsetHigh;
            } DUMMYSTRUCTNAME;
            PVOID Pointer;
        } DUMMYUNIONNAME;
         HANDLE hEvent;
} OVERLAPPED, *LPOVERLAPPED;



BOOL GetQueuedCompletionStatus(HANDLE, LPDWORD, PULONG_PTR, LPOVERLAPPED*);


""")

lib = ffi.dlopen(ctypes.util.find_library("c"))

def GetQueuedCompletionStatus(port, timeout):
    lib.GetQueuedCompletionStatus()
