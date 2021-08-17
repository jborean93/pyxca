# Copyright: (c) 2021 Jordan Borean (@jborean93) <jborean93@gmail.com>
# MIT License (see LICENSE or https://opensource.org/licenses/MIT)

"""XPRESS (LZ77) + Huffman.

Contains the necessary bindings to compress/decompress data with the
XPRESS+Huffman algorithm. The implementation defined in xpress.c is written
by Microsoft and slightly tweaked from the implementation in
`psl-omi-provider`_.

.. _psl-omi-provider:
    https://github.com/PowerShell/psl-omi-provider/blob/master/src/xpress.c
"""

import typing

from xca._xpress_huffman.bridge import (
    BadCompressionBuffer,
    BufferTooSmall,
    InvalidUserBuffer,
    XpressHuffmanException,
    XpressHuffmanWorkspace,
    compress_buffer_progress,
    decompress_buffer_progress,
)


class XpressHuffman:
    """XPRESS + Huffman algorithm.

    This is the public class that exposes a method to compress/decompress data
    using the XPRESS+Huffman algorithm.
    """

    def __init__(self) -> None:
        self._compressor: typing.Optional[XpressHuffmanWorkspace] = None
        self._decompressor: typing.Optional[XpressHuffmanWorkspace] = None

    def compress(
        self,
        data: typing.Union[bytes, bytearray, memoryview],
    ) -> bytes:
        """Compress data.

        Compresses the input data with XPRESS+Huffman.

        Args:
            data: The data to compress.

        Returns:
            bytes: The compressed data.
        """
        if not self._compressor:
            self._compressor = XpressHuffmanWorkspace.compressor()

        if isinstance(data, (bytearray, memoryview)):
            input = data
        else:
            input = bytearray(data)

        # xpress.c has a min length check of 300 so we include that + the length of the input data.
        output = bytearray(300 + len(data))
        length = compress_buffer_progress(input, output, self._compressor)

        return bytes(output[:length])

    def decompress(
        self,
        data: typing.Union[bytes, bytearray, memoryview],
        length: int,
    ) -> bytes:
        """Decompress data.

        Decompresses the input data with XPRESS+Huffman. The length of the
        decompressed data should be communicated using an application specific
        mechanism.

        Args:
            data: The data to decompress.
            length: The length of the plaintext data.

        Returns:
            bytes: The decompressed data.
        """
        if not self._decompressor:
            self._decompressor = XpressHuffmanWorkspace.decompressor()

        if isinstance(data, (bytearray, memoryview)):
            input = data
        else:
            input = bytearray(data)

        output = bytearray(length)
        length = decompress_buffer_progress(input, output, self._decompressor)

        return bytes(output[:length])


__all__ = [
    "BadCompressionBuffer",
    "BufferTooSmall",
    "InvalidUserBuffer",
    "XpressHuffmanException",
    "XpressHuffman",
]
