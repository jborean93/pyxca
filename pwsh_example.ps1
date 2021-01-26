$ErrorActionPreference = 'Stop'

Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;

public class Compression
{
    [DllImport("/home/jborean/dev/pyxca/libxpress.so")]
    public static extern UInt32 CompressWorkSpaceSizeXpressHuff(
        ref UInt32 CompressBufferWorkspaceSize,
        ref UInt32 DecompressBufferWorkspaceSize);

    [DllImport("/home/jborean/dev/pyxca/libxpress.so")]
    public static extern UInt32 DecompressBufferProgress(
        IntPtr UncompressedBuffer,
        UInt32 UncompressedBufferSize,
        IntPtr CompressedBuffer,
        UInt32 CompressedBufferSize,
        ref UInt32 FinalUncompressedSize,
        IntPtr Workspace,
        IntPtr Callback,
        IntPtr CallbackContext,
        UInt32 ProgressBytes);
}
'@

#$data = [Convert]::FromBase64String('/38MAUQAAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABEAAAAAAAAAAAAAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEAAAAAAAAAAAAAANDAAAAAAAAAAAAAAAAAAMAMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABMg80StOwA8P/mfwAA')
#$data = [Convert]::FromBase64String('/38uAWMGBWAAAAAABQAAAAAAAAAAYAAABmAAAGBgAGBlAAYGAAYAAAAAUAAAYAAABgAGAAAAAABmYAYAAAAAAAAAAGBgAAYAAAYAAAAAAAAGAAAAAAAAAAAAAAYAAAAAAGAAYAAAAGAAAAAAYABgAAAAAAYAAAYGAGAAYGAAAABQAAAABlUAAAAAAAAAAAAAAAAAUAUAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABxClqC7wKCGIIUzZjvM3xE1IsjGFmEbbZH/cUn997XtO7DyZq1PLdWAOD/uH8AAA==')
$data = [Convert]::FromBase64String('ClHlwBgAoAQAAgAAAAAAAAACAAAAAAAABwEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAgAAAAAAABAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAmAAA//wB')

$originalLength = [BitConverter]::ToInt16($data, 0) + 1
$compressedLength = [BitConverter]::ToInt16($data, 2) + 1
$offset = 4

$num = 0
while ($true) {
    write-host $num
    $originalLength = $num
    $compressedLength = $data.Length
    $offset = 0
    
    $compressSize = 0
    $decompressSize = 0
    $null = [Compression]::CompressWorkSpaceSizeXpressHuff([ref]$compressSize, [ref]$decompressSize)
    $workspace = [Runtime.InteropServices.Marshal]::AllocHGlobal($decompressSize)
    try {
        $toBuffer = [Runtime.InteropServices.Marshal]::AllocHGlobal($originalLength)
        $fromBuffer = [Runtime.InteropServices.Marshal]::AllocHGlobal($compressedLength)
        
        $bufferUsed = 0
        try {
            [Runtime.InteropServices.Marshal]::Copy($data, $offset, $fromBuffer, $data.Length - $offset)
    
            $res = [Compression]::DecompressBufferProgress(
                $toBuffer,
                $originalLength,
                $fromBuffer,
                $compressedLength,
                [ref]$bufferUsed,
                $workspace,
                [IntPtr]::Zero,
                [IntPtr]::Zero,
                0
            )
    
            if ($res -ne 0) {
                #throw "Failed to decompress data: $res"
                $num = $num + 1
                continue
            }
    
            $outputData = [byte[]]::new($bufferUsed)
            [Runtime.InteropServices.Marshal]::Copy($toBuffer, $outputData, 0, $bufferUsed)
            $outputString = [Text.Encoding]::UTF8.GetString($outputData)
            $a = ''
            break
    
        }
        finally {
            [Runtime.InteropServices.Marshal]::FreeHGlobal($toBuffer)
            [Runtime.InteropServices.Marshal]::FreeHGlobal($fromBuffer)
        }
    }
    finally {
        [Runtime.InteropServices.Marshal]::FreeHGlobal($workspace)
    }
    
}

$a = ''