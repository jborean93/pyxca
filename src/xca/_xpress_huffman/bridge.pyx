# Copyright: (c) 2021 Jordan Borean (@jborean93) <jborean93@gmail.com>
# MIT License (see LICENSE or https://opensource.org/licenses/MIT)

import typing

cimport cython
from libc.stdlib cimport free, malloc


cdef extern from "xpress.h":
    ctypedef unsigned int MI_Uint32

    unsigned int CompressBufferProgress(
        unsigned char *UncompressedBuffer,
        unsigned int UncompressedBufferSize,
        unsigned char *CompressedBuffer,
        unsigned int CompressedBufferSize,
        unsigned int *FinalCompressedSize,
        unsigned char *Workspace,
        void* Callback,
        void* CallbackContext,
        unsigned int ProgressBytes) nogil

    unsigned int DecompressBufferProgress(
        unsigned char *UncompressedBuffer,
        unsigned int UncompressedBufferSize,
        unsigned char *CompressedBuffer,
        unsigned int CompressedBufferSize,
        unsigned int *FinalUncompressedSize,
        unsigned char *Workspace,
        void* Callback,
        void* CallbackContext,
        unsigned int ProgressBytes) nogil

    unsigned int CompressWorkSpaceSizeXpressHuff(
        unsigned int *CompressBufferWorkSpaceSize,
        unsigned int *DecompressBufferWorkSpaceSize) nogil

    MI_Uint32 STATUS_SUCCESS
    MI_Uint32 STATUS_BUFFER_TOO_SMALL
    MI_Uint32 STATUS_INVALID_USER_BUFFER
    MI_Uint32 STATUS_BAD_COMPRESSION_BUFFER


cdef class XpressHuffmanWorkspace:

    cdef unsigned char* buffer

    def __cinit__(XpressHuffmanWorkspace self, unsigned int workspace_length):
        self.buffer = <unsigned char*>malloc(workspace_length)
        if not self.buffer:
            raise MemoryError()

    def __dealloc__(XpressHuffmanWorkspace self):
        if self.buffer:
            free(self.buffer)

    @staticmethod
    def compressor() -> XpressHuffmanWorkspace:
        return XpressHuffmanWorkspace(compress_workspace_size_xpress_huff()[0])

    @staticmethod
    def decompressor() -> XpressHuffmanWorkspace:
        return XpressHuffmanWorkspace(compress_workspace_size_xpress_huff()[1])


class XpressHuffmanException(Exception):
    pass


class BufferTooSmall(XpressHuffmanException):

    def __init__(self) -> None:
        super().__init__("Buffer too small to hold data")


class InvalidUserBuffer(XpressHuffmanException):

    def __init__(self) -> None:
        super().__init__("No workspace buffer has been provided")


class BadCompressionBuffer(XpressHuffmanException):

    def __init__(self) -> None:
        super().__init__("The input buffer is ill-formed")


def _check_return(res) -> None:
    if res == STATUS_BUFFER_TOO_SMALL:
        raise BufferTooSmall()

    elif res == STATUS_INVALID_USER_BUFFER:
        raise InvalidUserBuffer()

    elif res == STATUS_BAD_COMPRESSION_BUFFER:
        raise BadCompressionBuffer()


@cython.boundscheck(False)
@cython.wraparound(False)
def compress_buffer_progress(
    unsigned char[:] from_buffer not None,
    unsigned char[:] to_buffer not None,
    XpressHuffmanWorkspace workspace not None,
) -> int:
    cdef unsigned int final_size = 0
    cdef unsigned int from_size = <unsigned int><size_t>len(from_buffer)
    cdef unsigned int to_size = <unsigned int><size_t>len(to_buffer)
    cdef unsigned int res = 0

    with nogil:
        res = CompressBufferProgress(
            &from_buffer[0],
            from_size,
            &to_buffer[0],
            to_size,
            &final_size,
            workspace.buffer,
            NULL,
            NULL,
            0
        )

    _check_return(res)

    return final_size


@cython.boundscheck(False)
@cython.wraparound(False)
def decompress_buffer_progress(
    unsigned char[:] from_buffer not None,
    unsigned char[:] to_buffer not None,
    XpressHuffmanWorkspace workspace not None,
) -> int:
    cdef unsigned int final_size = 0
    cdef unsigned int from_size = <unsigned int><size_t>len(from_buffer)
    cdef unsigned int to_size = <unsigned int><size_t>len(to_buffer)
    cdef unsigned int res = 0

    with nogil:
        res = DecompressBufferProgress(
            &to_buffer[0],
            to_size,
            &from_buffer[0],
            from_size,
            &final_size,
            workspace.buffer,
            NULL,
            NULL,
            0
        )

    _check_return(res)

    return final_size


def compress_workspace_size_xpress_huff() -> typing.Tuple[int, int]:
    cdef unsigned int compress_size = 0
    cdef unsigned int decompress_size = 0

    CompressWorkSpaceSizeXpressHuff(&compress_size, &decompress_size)

    return compress_size, decompress_size
