#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Clonefinder

# The MIT License
#
# Copyright (c) 2010,2011,2012,2013,2015 Jeremie DECOCK (http://www.jdhp.org)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

"""
This module contains some tools to compute the hashes (or message digest) of a
file.

See https://docs.python.org/3/library/hashlib.html for more information.
"""

__all__ = ['compute_files_hash',
           'md5sum',
           'sha1sum',
           'sha256sum',
           'sha512sum']

import hashlib
import os

# TODO: profile the message digest with different chunk sizes
DEFAULT_CHUNK_SIZE = 2**12


def compute_files_hash(hash_generator,
                       file_path,
                       chunk_size=DEFAULT_CHUNK_SIZE):
    """Return the hash of a given file.

    :param string file_path: the path of the file for which the hash is
        computed.
    """

    if os.path.isfile(file_path): # TODO: exception !!!

        with open(file_path, 'rb') as fd:
            data = fd.read(chunk_size)
            while len(data) > 0:
                hash_generator.update(data)
                data = fd.read(chunk_size)

    hash_hex_str = hash_generator.hexdigest()

    return hash_hex_str


def md5sum(file_path, chunk_size=DEFAULT_CHUNK_SIZE):
    """Return the MD5 hash of a given file.

    :param string file_path: the path of the file for which the message digest
        is computed.
    """

    hash_generator = hashlib.md5()
    hash_hex_str = compute_files_hash(hash_generator, file_path, chunk_size)

    return hash_hex_str


def sha1sum(file_path, chunk_size=DEFAULT_CHUNK_SIZE):
    """Return the SHA1 hash of a given file.

    :param string file_path: the path of the file for which the hash is
        computed.
    """

    hash_generator = hashlib.sha1()
    hash_hex_str = compute_files_hash(hash_generator, file_path, chunk_size)

    return hash_hex_str


def sha256sum(file_path, chunk_size=DEFAULT_CHUNK_SIZE):
    """Return the SHA256 hash of a given file.

    :param string file_path: the path of the file for which the hash is
        computed.
    """

    hash_generator = hashlib.sha256()
    hash_hex_str = compute_files_hash(hash_generator, file_path, chunk_size)

    return hash_hex_str


def sha512sum(file_path, chunk_size=DEFAULT_CHUNK_SIZE):
    """Return the SHA512 hash of a given file.

    :param string file_path: the path of the file for which the hash is
        computed.
    """

    hash_generator = hashlib.sha512()
    hash_hex_str = compute_files_hash(hash_generator, file_path, chunk_size)

    return hash_hex_str

