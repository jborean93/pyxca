# Copyright: (c) 2021 Jordan Borean (@jborean93) <jborean93@gmail.com>
# MIT License (see LICENSE or https://opensource.org/licenses/MIT)

import typing

class XpressHuffmanException(Exception):
    """Base exception for XPRESS+Huffman compression."""

class BufferTooSmall(XpressHuffmanException):
    """Input buffer is too small."""

class InvalidUserBuffer(XpressHuffmanException):
    """The workspace buffer is not valid."""

class BadCompressionBuffer(XpressHuffmanException):
    """The input buffer is ill-formed."""

class XpressHuffmanWorkspace:
    """XPRESS+Huffman workspace."""

    def __init__(self, workspace_length: int) -> None: ...
    @staticmethod
    def compressor() -> XpressHuffmanWorkspace: ...
    @staticmethod
    def decompressor() -> XpressHuffmanWorkspace: ...

def compress_buffer_progress(
    from_buffer: typing.Union[bytearray, memoryview],
    to_buffer: typing.Union[bytearray, memoryview],
    workspace: XpressHuffmanWorkspace,
) -> int:
    """Compress data with XPRESS+Huffman encoding."""

def decompress_buffer_progress(
    from_buffer: typing.Union[bytearray, memoryview],
    to_buffer: typing.Union[bytearray, memoryview],
    workspace: XpressHuffmanWorkspace,
) -> int:
    """Decompress XPRESS+Huffman data."""

def compress_workspace_size_xpress_huff() -> typing.Tuple[int, int]:
    """Get the workspace size for XPRESS+Huffman."""
