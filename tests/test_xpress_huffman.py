# Copyright: (c) 2021 Jordan Borean (@jborean93) <jborean93@gmail.com>
# MIT License (see LICENSE or https://opensource.org/licenses/MIT)

import base64
import os

import pytest

import xca

from .conftest import CompressionFormat, WinCompressor

# https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-xca/f59ff967-3032-4331-b108-0d2b4c09ee27
TEST_CASES = {
    "simple": (
        b"abcdefghijklmnopqrstuvwxyz",
        b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        b"\x50\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x45\x44\x04\x00\x00"
        b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        b"\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        b"\xd8\x52\x3e\xd7\x94\x11\x5b\xe9\x19\x5f\xf9\xd6\x7c\xdf\x8d\x04"
        b"\x00\x00\x00\x00",
    ),
    "pattern": (
        b"abc" * 100,
        b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        b"\x30\x23\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        b"\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x20"
        b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
        b"\xa8\xdc\x00\x00\xff\x26\x01",
    ),
}


@pytest.mark.parametrize("uncompressed, expected", TEST_CASES.values(), ids=TEST_CASES.keys())
def test_xpress_huffman_compress(uncompressed: bytes, expected: bytes) -> None:
    xpress = xca.XpressHuffman()
    actual = xpress.compress(uncompressed)

    assert isinstance(actual, bytes)
    assert actual == expected


def test_xpress_huffman_compress_bytearray() -> None:
    input, expected = next(iter(TEST_CASES.values()))

    xpress = xca.XpressHuffman()
    actual = xpress.compress(bytearray(input))
    assert isinstance(actual, bytes)
    assert actual == expected


def test_xpress_huffman_compress_memoryview() -> None:
    input, expected = next(iter(TEST_CASES.values()))
    input = bytearray(input)

    xpress = xca.XpressHuffman()
    actual = xpress.compress(memoryview(input))
    assert isinstance(actual, bytes)
    assert actual == expected


@pytest.mark.parametrize("expected, compressed", TEST_CASES.values(), ids=TEST_CASES.keys())
def test_xpress_huffman_decompress(expected: bytes, compressed: bytes) -> None:
    xpress = xca.XpressHuffman()
    actual = xpress.decompress(compressed, len(expected))

    assert isinstance(actual, bytes)
    assert actual == expected


def test_xpress_huffman_decompress_bytearray() -> None:
    expected, input = next(iter(TEST_CASES.values()))

    xpress = xca.XpressHuffman()
    actual = xpress.decompress(bytearray(input), len(expected))
    assert isinstance(actual, bytes)
    assert actual == expected


def test_xpress_huffman_decompress_memoryview() -> None:
    expected, input = next(iter(TEST_CASES.values()))
    input = bytearray(input)

    xpress = xca.XpressHuffman()
    actual = xpress.decompress(memoryview(input), len(expected))
    assert isinstance(actual, bytes)
    assert actual == expected


def test_xpress_huffman_invalid_buffer() -> None:
    xpress = xca.XpressHuffman()

    with pytest.raises(xca.BadCompressionBuffer, match="The input buffer is ill-formed"):
        xpress.decompress(b"invalid", 1024)


@pytest.mark.parametrize("size", [1, 1024, 102, 23900, 56000, 8192])
def test_xpress_huffman_compress_random(size: int, win_compress: WinCompressor) -> None:
    data = os.urandom(size)

    compressed = xca.XpressHuffman().compress(data)
    actual = win_compress.decompress(CompressionFormat.xpress_huff, compressed, len(data))

    assert actual == data, f"Failed with input {base64.b64encode(data).decode()}"


@pytest.mark.parametrize("size", [1, 1024, 102, 23900, 56000, 8192])
def test_xpress_huffman_decompress_random(size: int, win_compress: WinCompressor) -> None:
    data = os.urandom(size)

    win_res = win_compress.compress(CompressionFormat.xpress_huff, data)
    actual = xca.XpressHuffman().decompress(win_res, len(data))

    assert actual == data, f"Failed with input {base64.b64encode(data).decode()}"
