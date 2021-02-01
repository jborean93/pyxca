import base64
import struct
import zlib


def compress(
    data: bytes,
) -> bytes:
    # https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-xca/b66751f2-be7b-4d20-a87c-5147c563ff2d
    output_bytes = bytearray(1024)

    flags = 0
    flag_count = 0
    flag_output_position = 0
    output_position = 4
    input_position = 0
    last_length_half_byte = 0

    while input_position != len(data):
        # Try to find a match with a length of at least 3 (see section 2.1.4.1)
        # The match must be within the last 8,192 bytes (MatchOffset <= 2^13)
        match_length = 0
        match_offset = 0

        # If no match was found or InputPosition +2 is beyond the input buffer
        if True:
            output_bytes[output_position] = data[input_position]
            output_position += 1
            input_position += 1

            flags <<= 1
            flag_count += 1
            if flag_count == 32:
                flags = struct.pack("<I", flags)
                flag_count = 0
                flag_output_position = output_position
                output_position += 4

        else:  # A valid match was found
            match_length -= 3
            match_offset -= 1
            match_offset <<= 3

            if match_length < 7:
                # This is the simple case. The length fits in 3 bits
                match_offset += match_length
                output_bytes[output_position:output_position + 2] = struct.pack("<H", match_offset)
                output_position += 2

            else:
                # The length does not fit 3 bits. Record a special value to indicate a longer length.
                match_offset |= 7
                output_bytes[output_position:output_position + 2] = struct.pack("<H", match_offset)
                output_position += 2

                match_length -= 7
                # Try to encode the length in the next 4 bits. If we previously
                # encoded a 4-bit length, we'll use the high 4 bits from that byte.
                if last_length_half_byte == 0:
                    last_length_half_byte = output_position
                    if match_length < 15:
                        output_bytes[output_position] = struct.pack("B", match_length)
                        output_position += 1
                    else:
                        output_bytes[output_position] = 15
                        output_position += 1
                        # goto EncodeExtraLen
                else:
                    if match_length < 15:
                        output_bytes[last_length_ha]
                a = ''
            a = ''

        a = ''

    return bytes(output_bytes[:output_position])


def decompress(
    data: bytes,
) -> bytes:
    # https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-xca/34cb9ab9-5ce6-42d7-a518-107c1c7c65e7
    output_bytes = bytearray(1024)

    buffered_flags = 0
    buffered_flag_count = 0
    input_position = 0
    output_position = 0
    last_length_half_byte = 0

    while True:
        if buffered_flag_count == 0:
            buffered_flags = struct.unpack("<I", data[input_position:input_position + 4])[0]
            input_position += 4
            buffered_flag_count = 32

        buffered_flag_count -= 1
        if buffered_flags & (1 << buffered_flag_count) == 0:
            output_bytes[output_position] = data[input_position]
            output_position += 1
            input_position += 1

        else:
            if input_position == len(data):
                break

            match_bytes = struct.unpack("<H", data[input_position:input_position + 2])[0]
            input_position += 2
            match_length = match_bytes % 8
            match_offset = (match_bytes // 8) + 1

            if match_length == 7:
                if last_length_half_byte == 0:
                    match_length = data[input_position]
                    match_length = match_length % 16
                    last_length_half_byte = input_position
                    input_position += 1

                else:
                    match_length = data[last_length_half_byte]
                    match_length = match_length // 16
                    last_length_half_byte = 0

                if match_length == 15:
                    match_length = data[input_position]
                    input_position += 1

                    if match_length == 255:
                        match_length = struct.unpack("<H", data[input_position:input_position + 2])[0]
                        input_position += 2
                        if match_length == 0:
                            match_length = struct.unpack("<I", data[input_position:input_position + 4])[0]
                            input_position += 4

                        if match_length < (15 + 7):
                            raise Exception()

                        match_length -= (15 + 7)

                    match_length += 15
                match_length += 7
            match_length += 3

            for i in range(0, match_length):
                output_bytes[output_position] = output_bytes[output_position - match_offset]
                output_position += 1

    return bytes(output_bytes[:output_position])


decompressed = b'abcdefghijklmnopqrstuvwxyz'
compressed = b'\x3f\x00\x00\x00\x61\x62\x63\x64\x65\x66\x67\x68\x69\x6a\x6b\x6c\x6d\x6e\x6f\x70\x71\x72\x73\x74\x75\x76\x77\x78\x79\x7a'

actual = decompress(compressed)
assert actual == decompressed

actual = zlib.decompress(compressed)
assert actual == decompressed

decompressed = b'abcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabcabc'
compressed = b'\xff\xff\xff\x1f\x61\x62\x63\x17\x00\x0f\xff\x26\x01'

actual = decompress(compressed)
assert actual == decompressed


'''
 Flags = 0      // this is a 32-bit integer value
 FlagCount = 0
 FlagOutputPosition = 0
 OutputPosition = 4
 InputPosition = 0
 LastLengthHalfByte = 0
 While InputPosition has not reached the end of the input buffer
     Try to find a match with a length of at least 3 (see section 2.1.4.1)
     The match must be within the last 8,192 bytes (MatchOffset <= 2^13)
     If no match was found or InputPosition + 2 is beyond the input buffer
         Copy 1 byte from InputPosition to OutputPosition.  Advance both.
         Flags <<= 1
         FlagCount = FlagCount + 1
         If FlagCount == 32
             Write the 32-bit value Flags to FlagOutputPosition
             FlagCount = 0
             FlagOutputPosition = OutputPosition
             OutputPosition += 4
     Else    // a valid match was found
         Let MatchLength and MatchOffset describe the match
         MatchLength = MatchLength – 3
         MatchOffset = MatchOffset – 1
         MatchOffset <<= 3
         If MatchLength < 7
             // This is the simple case. The length fits in 3 bits.
             MatchOffset += MatchLength
             Write MatchOffset the 2-byte value to OutputPosition
             OutputPosition += 2
         Else
             // The length does not fit 3 bits. Record a special value to
             // indicate a longer length.
             MatchOffset |= 7
             Write MatchOffset the 2-byte value to OutputPosition
             OutputPosition += 2
  
             MatchLength -= 7
             // Try to encode the length in the next 4 bits. If we previously
             // encoded a 4-bit length, we'll use the high 4 bits from that byte.
             If LastLengthHalfByte == 0
                 LastLengthHalfByte = OutputPosition
                 If MatchLength < 15
                     Write single byte value of MatchLength to OutputPosition
                     OutputPosition += 1
                 Else
                     Write single byte value of 15 to OutputPosition
                     OutputPosition++
                     goto EncodeExtraLen
             Else
                 If MatchLength < 15
                     OutputBuffer[LastLengthHalfByte] |= MatchLength << 4
                     LastLengthHalfByte = 0
                 Else
                     OutputBuffer[LastLengthHalfByte] |= 15 << 4
                     LastLengthHalfByte = 0
         EncodeExtraLen:
                     // We've already used 3 bits + 4 bits to encode the length
                     // Next use the next byte.
                     MatchLength -= 15
  
                     If MatchLength < 255
                         Write single byte value of MatchLength to OutputPosition
                         OutputPosition += 1
                     Else
                         // Use two more bytes for the length
                         Write single byte value of 255 to OutputPosition
                         OutputPosition += 1
  
                         MatchLength += 7 + 15
  
                         If MatchLength < (1 << 16)
                             Write two-byte value MatchLength to OutputPosition
                             OutputPosition += 2
                         Else
                             Write two-byte value of 0 to OutputPosition
                             OutputPosition += 2
                             Write four-byte value of MatchLength to OutputPosition
                             OutputPosition += 4
         Flags = (Flags << 1) | 1
         FlagCount = FlagCount + 1
         If FlagCount == 32
             Write the 32-bit value Flags to FlagOutputPosition
             FlagCount = 0
             FlagOutputPosition = OutputPosition
             OutputPosition += 4
         Advance InputPosition to the first byte that was not in the match
 Endwhile
 Flags <<= (32 – FlagCount)
 Flags |= (1 << (32 – FlagCount)) - 1
 Write the 32-bit value Flags to FlagOutputPosition
 The final compressed size is the value of OutputPosition
'''
