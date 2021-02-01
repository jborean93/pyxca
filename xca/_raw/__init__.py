from .bridge import *


def compress(
    algorithm: XpressWorkspace,
    data: bytes,
) -> bytes:
    buffer = bytearray(256 + len(data))

    final_size = compress_buffer_progress(
        bytearray(data),
        buffer,
        algorithm,
    )

    return bytes(buffer[:final_size])


def decompress(
    algorithm: XpressWorkspace,
    data: bytes,
    uncompressed_length: int,
) -> bytes:
    buffer = bytearray(uncompressed_length)

    final_size = decompress_buffer_progress(
        bytearray(data),
        buffer,
        algorithm,
    )

    return bytes(buffer[:final_size])
