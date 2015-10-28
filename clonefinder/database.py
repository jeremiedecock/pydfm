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
This module contains some tools to manage databases of computed file hashes
(to speedup their future accesses).
"""

__all__ = ['get_default_db_path',
           'print_db',
           'clear_db']

import dbm.dumb
import os

def get_default_db_path():
    """Return the default database path."""

    # A cross-platform way to get the current user's home directory
    home_dir = os.path.expanduser("~")
    default_db_filename = ".clonefinder"
    db_path = os.path.join(home_dir, default_db_filename)

    return db_path


def print_db(db_path):
    """Print the database content."""

    if db_path is not None:
        db = dbm.dumb.open(db_path, 'c')

        if len(db) == 0:
            print("Empty database.")
        else:
            for file_path, file_attributes in list(db.items()):
                file_mtime, file_size, file_md5 = file_attributes.split()
                print("{path} {mtime} {size} {md5}".format(path=file_path,
                                                           mtime=file_mtime,
                                                           size=file_size,
                                                           md5=file_md5))
            print(len(db), "files are recorded in", db_path)

        db.close()
    else:
        print("No database.")


def clear_db(db_path):
    """Remove the database content."""

    if db_path is not None:
        print("Clear ", db_path)
        #db = dbm.dumb.open(db_path, 'n')  # TODO: it doesn't work...
        db = dbm.dumb.open(db_path, 'c')
        db.clear()
        db.close()
    else:
        print("No database.")

