import pytest

import base64
import xca


def test_decompress():
    # https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-xca/f59ff967-3032-4331-b108-0d2b4c09ee27
    expected = b'abcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabc'
    compressed = base64.b64encode(base64.b16decode('00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000030230000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000200000000000000000000000000002000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000a8dc0000ff2601'.upper())).decode()

    plaintext_length = 300

    compressed_buffer = bytearray(compressed)
    decompressed_buffer = bytearray(plaintext_length)
    workspace = xca.XpressWorkspace.decompressor()

    final_size = xca.decompress_buffer_progress(
        compressed_buffer,
        decompressed_buffer,
        workspace)
    )

    actual = bytes(decompressed_buffer[:final_size])
    assert actual == expected
