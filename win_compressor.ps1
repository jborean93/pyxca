$ErrorActionPreference = 'Stop'

Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;

public enum CompressionAlgorithm
{
    MSZip = 2,
    Xpress = 3,
    XpressHuff = 4,
    Lzms = 5,
}

public class Compression
{
    [DllImport("Cabinet.dll")]
    public static extern bool CloseCompressor(
        IntPtr CompressorHandle);

    [DllImport("Cabinet.dll")]
    public static extern bool CloseDecompressor(
        IntPtr DecompressorHandle);

    [DllImport("Cabinet.dll", SetLastError = true)]
    public static extern bool Compress(
        IntPtr CompressorHandle,
        IntPtr UncompressedData,
        UIntPtr UncompressedDataSize,
        IntPtr CompressedBuffer,
        UIntPtr CompressedBufferSize,
        out UIntPtr CompressedDataSize);

    [DllImport("Cabinet.dll", SetLastError = true)]
    public static extern bool CreateCompressor(
        CompressionAlgorithm Algorithm,
        IntPtr AllocationRoutines,
        out IntPtr CompressorHandle);

    [DllImport("Cabinet.dll", SetLastError = true)]
    public static extern bool CreateDecompressor(
        CompressionAlgorithm Algorithm,
        IntPtr AllocationRoutines,
        out IntPtr DeccompressorHandle);

    [DllImport("Cabinet.dll", SetLastError = true)]
    public static extern bool Decompress(
        IntPtr DecompressorHandle,
        IntPtr CompressedData,
        UIntPtr CompressedDataSize,
        IntPtr UncompressedBuffer,
        UIntPtr UncompressedBufferSize,
        out UIntPtr UncompressedDataSize);
}
'@

Function Compress-Data {
    [CmdletBinding()]
    param (
        [Parameter(Mandatory=$true)]
        [String]
        $Data,

        [CompressionAlgorithm]
        $Algorithm = 'XpressHuff'
    )

    $dataBytes = [Text.Encoding]::UTF8.GetBytes($Data)

    $handle = [IntPtr]::Zero
    $res = [Compression]::CreateCompressor(
        $Algorithm,
        [IntPtr]::Zero,
        [ref]$handle
    ); $err = [Runtime.InteropServices.Marshal]::GetLastWin32Error()

    if (-not $res) {
        throw [System.ComponentModel.Win32Exception]$err
        return
    }

    try {
        $inputPtr = [Runtime.InteropServices.Marshal]::AllocHGlobal($dataBytes.Length)
        try {
            [Runtime.InteropServices.Marshal]::Copy($dataBytes, 0, $inputPtr, $dataBytes.Length)
            $bytesNeeded = 0

            $null = [Compression]::Compress(
                $handle,
                $inputPtr,
                $dataBytes.Length,
                [IntPtr]::Zero,
                0,
                [ref]$bytesNeeded
            )

            $outputPtr = [Runtime.InteropServices.Marshal]::AllocHGlobal([uint32]$bytesNeeded)
            try {
                $res = [Compression]::Compress(
                    $handle,
                    $inputPtr,
                    $dataBytes.Length,
                    $outputPtr,
                    $bytesNeeded,
                    [ref]$bytesNeeded
                ); $err = [Runtime.InteropServices.Marshal]::GetLastWin32Error()

                if (-not $res) {
                    throw [System.ComponentModel.Win32Exception]$err
                    return
                }

                $outputBytes = [byte[]]::new([uint32]$bytesNeeded)
                [Runtime.InteropServices.Marshal]::Copy($outputPtr, $outputBytes, 0, $outputBytes.Length)

                ,$outputBytes
            }
            finally {
                [Runtime.InteropServices.Marshal]::FreeHGlobal($outputPtr)
            }
        }
        finally {
            [Runtime.InteropServices.Marshal]::FreeHGlobal($inputPtr)
        }
    }
    finally {
        $null = [Compression]::CloseCompressor($handle)
    }
}

Function Decompress-Data {
    [CmdletBinding()]
    param (
        [Parameter(Mandatory=$true)]
        [byte[]]
        $Data,

        [CompressionAlgorithm]
        $Algorithm = 'XpressHuff'
    )

    $handle = [IntPtr]::Zero
    $res = [Compression]::CreateDecompressor(
        $Algorithm,
        [IntPtr]::Zero,
        [ref]$handle
    ); $err = [Runtime.InteropServices.Marshal]::GetLastWin32Error()

    if (-not $res) {
        throw [System.ComponentModel.Win32Exception]$err
        return
    }

    try {
        $inputPtr = [Runtime.InteropServices.Marshal]::AllocHGlobal($Data.Length)
        try {
            [Runtime.InteropServices.Marshal]::Copy($Data, 0, $inputPtr, $Data.Length)
            $bytesNeeded = 0

            $null = [Compression]::Decompress(
                $handle,
                $inputPtr,
                $Data.Length,
                [IntPtr]::Zero,
                0,
                [ref]$bytesNeeded
            )

            $outputPtr = [Runtime.InteropServices.Marshal]::AllocHGlobal([uint32]$bytesNeeded)
            try {
                $res = [Compression]::Decompress(
                    $handle,
                    $inputPtr,
                    $Data.Length,
                    $outputPtr,
                    $bytesNeeded,
                    [ref]$bytesNeeded
                ); $err = [Runtime.InteropServices.Marshal]::GetLastWin32Error()

                if (-not $res) {
                    throw [System.ComponentModel.Win32Exception]$err
                    return
                }

                $outputBytes = [byte[]]::new([uint32]$bytesNeeded)
                [Runtime.InteropServices.Marshal]::Copy($outputPtr, $outputBytes, 0, $outputBytes.Length)

                [Text.Encoding]::UTF8.GetString($outputBytes)
            }
            finally {
                [Runtime.InteropServices.Marshal]::FreeHGlobal($outputPtr)
            }
        }
        finally {
            [Runtime.InteropServices.Marshal]::FreeHGlobal($inputPtr)
        }
    }
    finally {
        $null = [Compression]::CloseDecompressor($handle)
    }
}

$data = 'a' * 128KB

$compressed = Compress-Data -Data $data
[Convert]::ToBase64String($compressed)

$decompressed = Decompress-Data -Data $compressed

$a = ''
