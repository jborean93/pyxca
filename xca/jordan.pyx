import typing

from libc.stdlib cimport (
    calloc,
    free,
    malloc,
)


cdef class XpressWorkspace:

    cdef unsigned char* buffer

    def __cinit__(XpressWorkspace self, unsigned int workspace_length):
        self.buffer = <unsigned char*>malloc(workspace_length)
        if not self.buffer:
            raise MemoryError()

    def __dealloc__(XpressWorkspace self):
        if self.buffer:
            free(self.buffer)

    @staticmethod
    def compressor() -> XpressWorkspace:
        return XpressWorkspace(compress_workspace_size_xpress_huff()[0])

    @staticmethod
    def decompressor() -> XpressWorkspace:
        return XpressWorkspace(compress_workspace_size_xpress_huff()[1])


cdef extern from "xpress.h":
    unsigned int CompressBufferProgress(
        unsigned char* UncompressedBuffer,
        unsigned int UncompressedBufferSize,
        unsigned char* CompressedBuffer,
        unsigned int CompressedBufferSize,
        unsigned int* FinalCompressedSize,
        unsigned char* Workspace,
        void* Callback,
        void* CallbackContext,
        unsigned int ProgressBytes) nogil

    unsigned int DecompressBufferProgress(
        unsigned char* UncompressedBuffer,
        unsigned int UncompressedBufferSize,
        unsigned char* CompressedBuffer,
        unsigned int CompressedBufferSize,
        unsigned int* FinalUncompressedSize,
        unsigned char* Workspace,
        void* Callback,
        void* CallbackContext,
        unsigned int ProgressBytes) nogil

    unsigned int CompressWorkSpaceSizeXpressHuff(
        unsigned int* CompressBufferWorkSpaceSize,
        unsigned int* DecompressBufferWorkSpaceSize) nogil


def compess_buffer_progress(
    unsigned char[:] from_buffer not None,
    unsigned char[:] to_buffer not None,
    XpressWorkspace workspace not None,
) -> int:
    cdef unsigned int final_size = 0
    cdef unsigned int from_size = len(from_buffer)
    cdef unsigned int to_size = len(to_buffer)
    cdef unsigned char* workspace_buffer = workspace.buffer
    cdef unsigned int res = 0

    with nogil:
        res = CompressBufferProgress(
            &to_buffer[0],
            to_size,
            &from_buffer[0],
            from_size,
            &final_size,
            workspace_buffer,
            NULL,
            NULL,
            0
        )

    if res != 0:
        raise Exception('failure: %s' % res)

    return final_size


def decompress_buffer_progress(
    unsigned char[:] from_buffer not None,
    unsigned char[:] to_buffer not None,
    XpressWorkspace workspace not None,
) -> int:
    cdef unsigned int final_size = 0
    cdef unsigned int from_size = len(from_buffer)
    cdef unsigned int to_size = len(to_buffer)
    cdef unsigned char* workspace_buffer = workspace.buffer
    cdef unsigned int res = 0

    with nogil:
        res = DecompressBufferProgress(
            &to_buffer[0],
            to_size,
            &from_buffer[0],
            from_size,
            &final_size,
            workspace_buffer,
            NULL,
            NULL,
            0
        )

    if res != 0:
        raise Exception('failure: %s' % res)

    #print(final_size)

    #return <bytes>(to_buffer[:final_size])
    return final_size


def compress_workspace_size_xpress_huff() -> typing.Tuple[int, int]:
    cdef unsigned int compress_size = 0
    cdef unsigned int decompress_size = 0

    with nogil:
        CompressWorkSpaceSizeXpressHuff(&compress_size, &decompress_size)

    return compress_size, decompress_size
