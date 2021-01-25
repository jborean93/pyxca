Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;

[StructLayout(LayoutKind.Sequential)]
public class DecodeBuffer
{
    public IntPtr buffer;
    public UInt32 bufferLength;
    public UInt32 bufferUsed;
}

public class Compression
{
    [DllImport("/home/jborean/dev/omi/PSWSMan/lib/fedora33/libpsrpclient.so")]
    public static extern UInt32 DecompressBuffer(
        DecodeBuffer fromBuffer,
        DecodeBuffer toBuffer);
}
'@

$data = [Convert]::FromBase64String('/38MAUQAAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABEAAAAAAAAAAAAAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEAAAAAAAAAAAAAANDAAAAAAAAAAAAAAAAAAMAMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABMg80StOwA8P/mfwAA')
#$data = [COnvert]::FromBase64String('/38uAWMGBWAAAAAABQAAAAAAAAAAYAAABmAAAGBgAGBlAAYGAAYAAAAAUAAAYAAABgAGAAAAAABmYAYAAAAAAAAAAGBgAAYAAAYAAAAAAAAGAAAAAAAAAAAAAAYAAAAAAGAAYAAAAGAAAAAAYABgAAAAAAYAAAYGAGAAYGAAAABQAAAABlUAAAAAAAAAAAAAAAAAUAUAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABxClqC7wKCGIIUzZjvM3xE1IsjGFmEbbZH/cUn997XtO7DyZq1PLdWAOD/uH8AAA==')

$inputDataPtr = [Runtime.InteropServices.Marshal]::AllocHGlobal($data.Length)

try {
    [Runtime.InteropServices.Marshal]::Copy($data, 0, $inputDataPtr, $data.Length)

    $inputBuffer = [DecodeBuffer]::new()
    $inputBuffer.buffer = $inputDataPtr
    $inputBuffer.bufferLength = $data.Length
    $inputBuffer.bufferUsed = $data.Length
    
    $outputBuffer = [DecodeBuffer]::new()
    $outputBuffer.buffer = [IntPtr]::Zero
    $outputBuffer.bufferLength = 0
    $outputBuffer.bufferUsed = 0

    $res = [Compression]::DecompressBuffer($inputBuffer, $outputBuffer)
    if ($res -ne 0) {
        throw "Failed to decompress"
    }

    $outputData = [byte[]]::new($outputBuffer.bufferUsed)
    [Runtime.InteropServices.Marshal]::Copy($outputBuffer.buffer, $outputData, 0, $outputData.Length)
    [Text.Encoding]::UTF8.GetString($outputData)
}
finally {
    [Runtime.InteropServices.Marshal]::FreeHGlobal($inputDataPtr)
}
