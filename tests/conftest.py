# Copyright: (c) 2021 Jordan Borean (@jborean93) <jborean93@gmail.com>
# MIT License (see LICENSE or https://opensource.org/licenses/MIT)

import ctypes
import enum
import os
import typing

import pytest


class CompressionFormat(enum.IntEnum):
    no_compression = 0x0000
    default = 0x0001
    lznt1 = 0x0002
    xpress = 0x0003
    xpress_huff = 0x0004


class CompressionEngine(enum.IntEnum):
    standard = 0x0000
    maximum = 0x0100
    hiber = 0x0200


class WinCompressor:
    def __init__(self) -> None:
        self.ntdll = getattr(ctypes, "windll").ntdll
        self.ntdll.RtlGetCompressionWorkSpaceSize.argtypes = (
            ctypes.c_int16,
            ctypes.POINTER(ctypes.c_uint32),
            ctypes.POINTER(ctypes.c_uint32),
        )
        self.ntdll.RtlGetCompressionWorkSpaceSize.restype = ctypes.c_uint32

        self.ntdll.RtlCompressBuffer.argtypes = (
            ctypes.c_uint16,
            ctypes.c_void_p,
            ctypes.c_uint32,
            ctypes.c_void_p,
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.POINTER(ctypes.c_uint32),
            ctypes.c_void_p,
        )
        self.ntdll.RtlCompressBuffer.restype = ctypes.c_uint32

        self.ntdll.RtlDecompressBufferEx.argtypes = (
            ctypes.c_uint16,
            ctypes.c_void_p,
            ctypes.c_uint32,
            ctypes.c_void_p,
            ctypes.c_uint32,
            ctypes.POINTER(ctypes.c_uint32),
            ctypes.c_void_p,
        )
        self.ntdll.RtlDecompressBufferEx.restype = ctypes.c_uint32

        self.ntdll.RtlNtStatusToDosError.argtypes = (ctypes.c_uint32,)
        self.ntdll.RtlNtStatusToDosError.restype = ctypes.c_uint32

        compress_size = ctypes.c_uint32(0)
        decompress_size = ctypes.c_uint32(0)
        self.ntdll.RtlGetCompressionWorkSpaceSize(
            CompressionFormat.xpress_huff | CompressionEngine.standard,
            ctypes.byref(compress_size),
            ctypes.byref(decompress_size),
        )
        self.compress_size = compress_size.value
        self.decompress_size = decompress_size.value

    def compress(
        self,
        data: bytes,
    ) -> bytes:
        workspace = ctypes.create_string_buffer(self.compress_size)
        output = ctypes.create_string_buffer(300 + len(data))
        compressed_size = ctypes.c_uint32(len(output))
        res = self.ntdll.RtlCompressBuffer(
            CompressionFormat.xpress_huff | CompressionEngine.standard,
            data,
            len(data),
            output,
            len(output),
            4096,
            ctypes.byref(compressed_size),
            workspace,
        )
        if res:
            raise getattr(ctypes, "WinError")(self.ntdll.RtlNtStatusToDosError(res))

        return output.raw[: compressed_size.value]

    def decompress(
        self,
        data: bytes,
        length: int,
    ) -> bytes:
        workspace = ctypes.create_string_buffer(self.decompress_size)
        output = ctypes.create_string_buffer(length)
        decompressed_size = ctypes.c_uint32(length)
        res = self.ntdll.RtlDecompressBufferEx(
            CompressionFormat.xpress_huff,
            output,
            length,
            data,
            len(data),
            ctypes.byref(decompressed_size),
            workspace,
        )
        if res:
            raise getattr(ctypes, "WinError")(self.ntdll.RtlNtStatusToDosError(res))

        return output.raw[: decompressed_size.value]


@pytest.fixture(scope="function")
def win_compress() -> typing.Iterable[WinCompressor]:
    if os.name != "nt":
        pytest.skip("Uses Win32 API")

    yield WinCompressor()
