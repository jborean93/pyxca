# Xpress Compression Library for Python

[![Test workflow](https://github.com/jborean93/pyxca/actions/workflows/ci.yml/badge.svg)](https://github.com/jborean93/pyxca/actions/workflows/ci.yml)
[![PyPI version](https://badge.fury.io/py/pyxca.svg)](https://badge.fury.io/py/pyxca)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/jborean93/pyxca/blob/main/LICENSE)

Implements Microsoft xpress compression for Python.
The Xpress algorithm is defined under [MS-XCA](https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-xca/a8b7cb0a-92a6-4187-a23b-5e14273b96f8) and encompasses 3 different algorithms

* LZ77 - Not implemented
* LZ77 + Huffman - Implemented
* LZNT1 - Not implemented

Currently only the Xpress + Huffman algorithm is implemented with the code being based on what Microsoft themselves has provided under the MIT license.

> :warning: **This library is experimental and is subject to change**: Be very careful here!

## Requirements

* Python 3.6+
* A C compiler, such as GCC

The compiler is only needed if installing from source/sdist, if using the wheel from PyPI then it should not be needed.

## Installation

Simply run:

```bash
pip install xca
```

To install from source run the following:

```bash
git clone https://github.com/jborean93/pyxca.git
pip install Cython
python setup.py bdist_wheel
pip install dist/xca-*.whl
```

## Development

To run the tests or make changes to this repo run the following:

```bash
git clone https://github.com/jborean93/pyxca.git
pip install -r requirements-dev.txt
pre-commit install

python setup.py build_ext --inplace
```

This will build the Cython and C code inplace where it can be imported by Python.
From there an editor like VSCode can be used to make changes and run the test suite.
To recompile the Cython files after a change run the `build_ext --inplace` command.

## Examples



```python
import xca

data = b"Hello World" * 1024
workspace = xca.XpressHuffman()

compressed_data = workspace.compress(data)

# The length of the plaintext should be communicated in some way to the decompressor
decompressed_data = workspace.decompress(compress_data, len(data))
```

## Backlog

* Implement Xpress/LZ77
* Implement LZNT1
* Do some performance testing
