# xpress library for Python

Implements Microsoft xpress compression for Python.
This is used by WinRM and SMB and is designed to expose an optimised library to compress/decompress data for libraries that implement those protocols.

There is an MIT licensed source for this algorithm at https://github.com/PowerShell/psl-omi-provider/blob/master/src/xpress.c.
My aim is to make this a standalone library that can be called in Python through something like Cython.
While the code has been tested against a WinRS response I'm hoping to see if it's also applicable for [SMB compression](https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-smb2/78e0c942-ab41-472b-b117-4a95ebe88271) potentially it's LZ77+Huffman.

# TODO

* extract xpress.c/xpress.h into a self compiled library
* tidy up xpress.c to remove extra cruft (do I actually want to do this?)
* create interface in Python to call these now public functions
* look at converting to cython
* create python library


# Compile

```bash
CFLAGS='-Wall -O0 -g' gcc -shared -o libxpress.so -fPIC xca/xpress.c

# Compile cython code
python setup.py clean --all build_ext --inplace

# Create debug binary
CFLAGS='-Wall -O0 -g' python setup.py clean --all build_ext --inplace

# nm -gD libxpress.so
```
