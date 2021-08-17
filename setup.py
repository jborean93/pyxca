#!/usr/bin/env python
# Copyright: (c) 2021 Jordan Borean (@jborean93) <jborean93@gmail.com>
# MIT License (see LICENSE or https://opensource.org/licenses/MIT)

import glob
import os
import os.path
import sys
import typing

from setuptools import Extension, find_packages, setup
from setuptools.command.sdist import sdist

SKIP_CYTHON_FILE = "__dont_use_cython__.txt"

if os.path.exists(SKIP_CYTHON_FILE):
    print("In distributed package, building from C files...")
    SOURCE_EXT = "c"
else:
    try:
        from Cython.Build import cythonize

        print("Building from Cython files...")
        SOURCE_EXT = "pyx"
    except ImportError:
        print("Cython not found, building from C files...")
        SOURCE_EXT = "c"


compiler_args = []
linker_args = []
if os.name == "nt":
    compiler_args.extend(["/WX", "-D_WINDOWS_"])
    linker_args.append("/WX")

else:
    compiler_args.append("-Werror")
    # Python 3.8 on macOS errors on these deprecation warnings. We ignore them as things are fixed on 3.9 but the
    # code still needs to compile on 3.8.
    if sys.platform == "darwin" and sys.version_info[:2] == (3, 8):
        compiler_args.append("-Wno-deprecated")

raw_extensions: typing.List[Extension] = []
for e in ["xpress_huffman"]:
    source_dir = os.path.join("src", "xca", f"_{e}")

    pyx_files: typing.Set[str] = set()
    c_files: typing.Set[str] = set()
    for name in os.listdir(source_dir):
        if name.endswith(".pyx"):
            pyx_files.add(name[:-4])
        elif name.endswith(".c"):
            c_files.add(name[:-2])

    c_files.difference_update(pyx_files)

    for module in pyx_files:
        name = f"xca._{e}.{module}"
        sources = [os.path.join(source_dir, f"{module}.{SOURCE_EXT}")]
        for c in c_files:
            sources.append(os.path.join(source_dir, f"{c}.c"))

        print(f"Compiling {name}")
        raw_extensions.append(
            Extension(
                name=name,
                sources=sources,
                extra_compile_args=compiler_args,
                extra_link_args=linker_args,
            )
        )

if SOURCE_EXT == "c":
    extensions = raw_extensions
else:
    extensions = cythonize(
        raw_extensions,
        language_level=3,
    )


with open(os.path.join(os.path.dirname(__file__), "README.md"), mode="rb") as fd:
    long_description = fd.read().decode("utf-8")


class sdist_xca(sdist):
    def run(self) -> None:
        if not self.dry_run:
            with open(SKIP_CYTHON_FILE, mode="wb") as flag_file:
                flag_file.write(b"")

            sdist.run(self)

            os.remove(SKIP_CYTHON_FILE)


setup(
    name="xca",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_data={
        "xca": ["py.typed", "**/*.pyi"],
    },
    package_dir={"": "src"},
    py_modules=[os.path.splitext(os.path.basename(path))[0] for path in glob.glob("src/*.py")],
    cmdclass={
        "sdist": sdist_xca,
    },
    ext_modules=extensions,
    include_package_data=False,
    install_requires=[],
    extras_require={},
    author="Jordan Borean",
    author_email="jborean93@gmail.com",
    url="https://github.com/jborean93/pyxca",
    description="Python wrapper for Microsoft xpress compression",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords="xca huffman",
    license="MIT",
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
