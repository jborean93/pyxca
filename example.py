import base64
import collections
import sys
import struct
import uuid
import xca


expected = b'abcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabc'
compressed = base64.b16decode('00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000030230000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000200000000000000000000000000002000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000a8dc0000ff2601'.upper())

plaintext_length = 300

compressed_buffer = bytearray(compressed)
decompressed_buffer = bytearray(plaintext_length)
workspace = xca.XpressWorkspace.decompressor()

final_size = xca.decompress_buffer_progress(
    compressed_buffer,
    decompressed_buffer,
    workspace,
)

actual = bytes(decompressed_buffer[:final_size])
assert actual == expected

# sys.exit(0)


Fragment = collections.namedtuple('Fragment', ['object_id', 'fragment_id', 'start', 'end', 'data'])
Message = collections.namedtuple('Message', ['destination', 'message_type', 'rpid', 'pid', 'data'])

def _unpack_fragment(
        data: bytearray,
) -> Fragment:
    """ Unpack a PSRP fragment into a structured format. """
    object_id = struct.unpack(">Q", data[0:8])[0]
    fragment_id = struct.unpack(">Q", data[8:16])[0]
    start_end_byte = struct.unpack("B", data[16:17])[0]
    start = start_end_byte & 0x1 == 0x1
    end = start_end_byte & 0x2 == 0x2
    length = struct.unpack(">I", data[17:21])[0]

    return Fragment(object_id, fragment_id, start, end, data[21:length + 21])


def _unpack_message(
        data: bytearray,
) -> Message:
    """ Unpack a PSRP message into a structured format. """
    destination = struct.unpack("<I", data[0:4])[0]
    message_type = struct.unpack("<I", data[4:8])[0]
    rpid = str(uuid.UUID(bytes_le=bytes(data[8:24]))).upper()
    pid = str(uuid.UUID(bytes_le=bytes(data[24:40]))).upper()

    if rpid == '00000000-0000-0000-0000-000000000000':
        rpid = None
    if pid == '00000000-0000-0000-0000-000000000000':
        pid = None

    data = data[40:]
    if data.startswith(b"\xEF\xBB\xBF"):
        data = data[3:]  # Handle UTF-8 BOM in data.

    return Message(destination, message_type, rpid, pid, data)


# Command '"hi" * 64KB'

responses = [
    # Are compressed, contains the pipeline output '<S>hihihihihi....'
    # 307 bytes
    '/38uAWMGBWAAAAAABQAAAAAAAAAAYAAABmAAAGBgAGBlAAYGAAYAAAAAUAAAYAAABgAGAAAAAABmYAYAAAAAAAAAAGBgAAYAAAYAAAAAAAAGAAAAAAAAAAAAAAYAAAAAAGAAYAAAAGAAAAAAYABgAAAAAAYAAAYGAGAAYGAAAABQAAAABlUAAAAAAAAAAAAAAAAAUAUAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABxClqC7wKCGIIUzZjvM3xE1IsjGFmEbbZH/cUn997XtO7DyZq1PLdWAOD/uH8AAA==',
    # 273 bytes
    '/38MAUQAAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABEAAAAAAAAAAAAAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEAAAAAAAAAAAAAANDAAAAAAAAAAAAAAAAAAMAMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABMg80StOwA8P/mfwAA',
    # 273 bytes
    '/38MAQQEAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABEAAAAAAAAAAAAAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEAAAAAAAAAAAAAANDAAAAAAAAAAAAAAAAAAMAMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABMg80SxOsA8P/mfwAA',
    # 273 bytes
    '/38MAQRAAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABEAAAAAAAAAAAAAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEAAAAAAAAAAAAAANDAAAAAAAAAAAAAAAAAAMAMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABMg80StOwA8P/mfwAA',

    #  The following are not compressed.
    # '...hihihihi</s>'
    # 159 bytes
    'mgCaAAAAAAAAAAAHAAAAAAAAAAQCAAAAhmhpaGloaWhpaGloaWhpaGloaWhpaGloaWhpaGloaWhpaGloaWhpaGloaWhpaGloaWhpaGloaWhpaGloaWhpaGloaWhpaGloaWhpaGloaWhpaGloaWhpaGloaWhpaGloaWhpaGloaWhpaGloaWhpaGloaWhpaGloaWhpaGloaWhpaGk8L1M+',
    # Contains pipeline state '<Obj RefId="0"><MS><I32 N="PipelineState">4</I32></MS></Obj>'
    # 128 bytes
    'ewB7AAAAAAAAAAAIAAAAAAAAAAADAAAAZwEAAAAGEAQAXDk4QisoN02YEOQxhPnV+WvHrgLxWN5NiiPm0Ww4gTPvu788T2JqIFJlZklkPSIwIj48TVM+PEkzMiBOPSJQaXBlbGluZVN0YXRlIj40PC9JMzI+PC9NUz48L09iaj4=',
]

# Hex of first 4 responses
# b'FF7F2E0163060560
# b'FF7F0C0144000040
# b'FF7F0C0104040040
# b'FF7F0C0104400040

# The first 4 bytes represent the length of the original message -1 and the length of the compressed message – 1. Anything smaller than 266 bytes is not compressed.
# 32767:302
# 32767:268
# 32767:268
# 32767:268

decompressed = []
workspace = xca.XpressWorkspace.decompressor()
for resp in responses:
    data = base64.b64decode(resp)

    to_size = struct.unpack('<H', data[0:2])[0] + 1
    from_size = struct.unpack('<H', data[2:4])[0] + 1
    #to_size = 300
    #from_size = len(data)

    if to_size == from_size:
        decompressed.append(data[4:])
        continue

    from_buffer = bytearray(data[4:from_size + 4])
    #from_buffer = bytearray(data)
    to_buffer = bytearray(to_size)

    final_size = xca.decompress_buffer_progress(
        from_buffer,
        to_buffer,
        workspace,
    )

    decompressed_data = bytes(to_buffer[:final_size])
    if to_buffer.endswith(b'\x00'):
        a = ''
    decompressed.append(decompressed_data)


fragment_buffer = {}
messages = []

for data in decompressed:
    fragment = _unpack_fragment(bytearray(data))

    if fragment.start:
        fragment_buffer[fragment.object_id] = bytearray()

    buffer = fragment_buffer[fragment.object_id]
    buffer += fragment.data

    if fragment.end:
        msg = _unpack_message(buffer)
        messages.append(msg)


expected = f'<S>{"hi" * 65536}</S>'
actual = bytes(messages[0].data)

print(len(actual))
print(len(expected))
print(actual)

assert len(actual) == len(expected)
assert actual == expected
