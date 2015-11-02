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
This module contains some unit tests for the file hashes utility functions
implemented in the "file_hash" module.
"""

from clonefinder import file_hash

import os.path
import unittest

TESTS_DIRNAME = os.path.dirname(__file__)
DATA_DIRNAME = os.path.join(TESTS_DIRNAME, "data")

class TestFileHash(unittest.TestCase):
    """
    Contains some unit tests for the file hashes utility functions implemented
    in the "file_hash" module.
    """

    # Check md5sum() ##########################################################

    def test_md5sum(self):
        """Check that the file_hash.md5sum function returns the right messages
        digest for some known test files."""

        # Test "data/test_file.txt"

        file_path = os.path.join(DATA_DIRNAME, "test_file.txt")

        expected_str = "335387a52cfc8f1d3fda510b12dfc200"
        hex_str = file_hash.md5sum(file_path)

        self.assertEqual(hex_str, expected_str)

        # Test "data/test_file.bin"

        file_path = os.path.join(DATA_DIRNAME, "test_file.bin")

        expected_str = "8c1379aa4207f5b4b801a49b75e826c8"
        hex_str = file_hash.md5sum(file_path)

        self.assertEqual(hex_str, expected_str)

        # Test "data/test_file.empty"

        file_path = os.path.join(DATA_DIRNAME, "test_file.empty")

        expected_str = "d41d8cd98f00b204e9800998ecf8427e"
        hex_str = file_hash.md5sum(file_path)

        self.assertEqual(hex_str, expected_str)

    # Check sha1sum() ##########################################################

    def test_sha1sum(self):
        """Check that the file_hash.sha1sum function returns the right hashes
        for some known test files."""

        # Test "data/test_file.txt"

        file_path = os.path.join(DATA_DIRNAME, "test_file.txt")

        expected_str = "b4283c4fbc88317115315f876743fd7580c29d4b"
        hex_str = file_hash.sha1sum(file_path)

        self.assertEqual(hex_str, expected_str)

        # Test "data/test_file.bin"

        file_path = os.path.join(DATA_DIRNAME, "test_file.bin")

        expected_str = "ff7bbd6d6841f319537b3ed8dc9f1236afd931b3"
        hex_str = file_hash.sha1sum(file_path)

        self.assertEqual(hex_str, expected_str)

        # Test "data/test_file.empty"

        file_path = os.path.join(DATA_DIRNAME, "test_file.empty")

        expected_str = "da39a3ee5e6b4b0d3255bfef95601890afd80709"
        hex_str = file_hash.sha1sum(file_path)

        self.assertEqual(hex_str, expected_str)

    # Check sha256sum() ##########################################################

    def test_sha256sum(self):
        """Check that the file_hash.sha256sum function returns the right hashes
        for some known test files."""

        # Test "data/test_file.txt"

        file_path = os.path.join(DATA_DIRNAME, "test_file.txt")

        expected_str = "53fabd3b1665f9aa789fd9473d93312d4f80ee16ad7eff73c6f59845ca476d94"
        hex_str = file_hash.sha256sum(file_path)

        self.assertEqual(hex_str, expected_str)

        # Test "data/test_file.bin"

        file_path = os.path.join(DATA_DIRNAME, "test_file.bin")

        expected_str = "313e519e72b34ff63fc0bc1a4d0ed056244e2d3af8863be89b3bc37f280a8282"
        hex_str = file_hash.sha256sum(file_path)

        self.assertEqual(hex_str, expected_str)

        # Test "data/test_file.empty"

        file_path = os.path.join(DATA_DIRNAME, "test_file.empty")

        expected_str = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        hex_str = file_hash.sha256sum(file_path)

        self.assertEqual(hex_str, expected_str)

    # Check sha512sum() ##########################################################

    def test_sha512sum(self):
        """Check that the file_hash.sha512sum function returns the right hashes
        for some known test files."""

        # Test "data/test_file.txt"

        file_path = os.path.join(DATA_DIRNAME, "test_file.txt")

        expected_str = "cda20ce1aad439986c151cc7b5002cee5c9cf5997381623ff6988e6d221d96968c71b79b6bab80226a262b8831538a6427cdd798ecabca76ed2de54b04081921"
        hex_str = file_hash.sha512sum(file_path)

        self.assertEqual(hex_str, expected_str)

        # Test "data/test_file.bin"

        file_path = os.path.join(DATA_DIRNAME, "test_file.bin")

        expected_str = "91af89302f34c9a477162836afbc6cd74b70216ffe6c5c04165aafdf81a2540e6908d46e5ea53247d2ece695fad84a99662fbdd8632357701285bc01c0cca8c6"
        hex_str = file_hash.sha512sum(file_path)

        self.assertEqual(hex_str, expected_str)

        # Test "data/test_file.empty"

        file_path = os.path.join(DATA_DIRNAME, "test_file.empty")

        expected_str = "cf83e1357eefb8bdf1542850d66d8007d620e4050b5715dc83f4a921d36ce9ce47d0d13c5d85f2b0ff8318d2877eec2f63b931bd47417a81a538327af927da3e"
        hex_str = file_hash.sha512sum(file_path)

        self.assertEqual(hex_str, expected_str)

if __name__ == '__main__':
    unittest.main()
