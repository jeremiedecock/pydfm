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

class TestFileHash(unittest.TestCase):
    """
    Contains some unit tests for the file hashes utility functions implemented
    in the "file_hash" module.
    """

    # Check md5sum() ##########################################################

    def test_md5sum(self):
        """Check that the file_hash.md5sum function returns the right message
        digest for a known test file."""

        #dirname = os.path.dirname(__loader__.get_filename())   # TODO: check...
        dirname = os.path.dirname(__file__)   # TODO: check...
        file_path = os.path.join(dirname, "test_file.txt")

        expected_str = "335387a52cfc8f1d3fda510b12dfc200"
        hex_str = file_hash.md5sum(file_path)

        self.assertEqual(hex_str, expected_str)

if __name__ == '__main__':
    unittest.main()
