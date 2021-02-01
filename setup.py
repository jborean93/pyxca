#!/usr/bin/env python

import os.path
import setuptools
import sys

from Cython.Build import cythonize
from distutils.core import setup, Extension
    
try:
    sys.argv.remove('--cython-linetrace')
    cython_linetrace = True
except ValueError:
    cython_linetrace = False


raw_path = os.path.join('xca', '_raw')

extensions = cythonize([
    Extension(
        name='xca._raw.bridge',
        sources=[
            os.path.join(raw_path, 'bridge.pyx'),
            os.path.join(raw_path, 'xpress.c'),
        ],
    ),
], language_level=3, compiler_directives={'linetrace': cython_linetrace})

setup(
    name='xca',
    version='1.0.0',
    description='Python wrapper for Microsoft xpress compession',
    author='Jordan Borean',
    author_email='jborean93@gmail.com',
    packages=[
        'xca',
        'xca._raw',
    ],
    ext_modules=extensions,
)
