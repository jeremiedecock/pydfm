#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2010,2011,2012 Jérémie DECOCK (http://www.jdhp.org)

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.



# http://www.techsupportalert.com/best-free-duplicate-file-detector.htm


import os
import sys
import time
import argparse
import hashlib

VERSION = "2.0"
COPYING = '''Copyright (c) 2010,2011,2012 Jeremie DECOCK (http://www.jdhp.org)
This is free software; see the source for copying conditions.
There is NO warranty; not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.'''

CHUNK_SIZE = 2**12

def main():
    """Main function"""

    # PARSE OPTIONS ###########################################################

    parser = argparse.ArgumentParser(description='Find duplicated files and directories.')

    parser.add_argument("--db", "-d", help="database path", metavar="STRING")
    parser.add_argument("--nodb", "-n", help="don't use database file", action="store_true")
    parser.add_argument("--version", "-v", action="version", version="%(prog)s " + VERSION)
    parser.add_argument("root_paths", nargs="+", metavar="DIRECTORY", help="root directory")

    args = parser.parse_args()

    for path in args.root_paths:
        if not os.path.isdir(path):
            print "ERROR: {0} is not a directory.".format(path)
            print parser.format_usage(),
            sys.exit(2)

    db_path = None
    if args.nodb:
        pass
    else:
        if args.db is None:
            db_path = get_default_db_path()
        else:
            db_path = args.db
            if not os.path.isfile(db_path):
                print "ERROR: {0} is not a file.".format(db_path)
                print parser.format_usage(),
                sys.exit(2)

    print db_path

    # COMPUTE HASHS ###########################################################

    # dict = {path: hash, ...}
    file_dict = {}
    dir_dict = {}

    # For each root path specified in command line argmuents
    for path in args.root_paths:

        # root =  a string, the path to the directory.
        # dirs =  a list of the names (strings) of the subdirectories in
        #         dirpath (excluding '.' and '..').
        # files = a list of the names (strings) of the non-directory files
        #         in dirpath.
        for root, dirs, files in os.walk(path, topdown=False):

            root_digest = hashlib.md5()

            for name in files:
                file_path = os.path.join(root, name)
                file_digest = md5sum(file_path)
                file_dict[file_path] = file_digest
                
                root_digest.update(file_digest)

            for name in dirs:
                dir_path = os.path.join(root, name)
                root_digest.update(dir_dict[dir_path])

            dir_dict[root] = root_digest.hexdigest()

    # BUILD REVERSE DICTIONNARY ###############################################

    # reverse_dict = {hash: [path1, path2, ...], ...}
    reverse_file_dict = {}

    for path, hash in file_dict.items():
        if not reverse_file_dict.has_key(hash):
            reverse_file_dict[hash] = []
        reverse_file_dict[hash].append(path)

    reverse_dir_dict = {}

    for path, hash in dir_dict.items():
        if not reverse_dir_dict.has_key(hash):
            reverse_dir_dict[hash] = []
        reverse_dir_dict[hash].append(path)

    # REMOVE REDUNDANT ENTRIES ################################################

    for dir_hash, dir_paths in reverse_dir_dict.items():
        if len(dir_paths) > 1:
            for file_hash, file_paths in reverse_file_dict.items():
                if len(file_paths) == len(dir_paths):
                    file_paths.sort()
                    dir_paths.sort()

                    redundant_entry = True
                    for dir_path, file_path in zip(dir_paths, file_paths):
                        if not file_path.startswith(dir_path):
                            redundant_entry = False 

                    if redundant_entry:
                        del reverse_file_dict[file_hash]
            for subdir_hash, subdir_paths in reverse_dir_dict.items():
                if (len(subdir_paths) == len(dir_paths)) and (subdir_paths is not dir_paths):
                    subdir_paths.sort()
                    dir_paths.sort()

                    redundant_entry = True
                    for dir_path, subdir_path in zip(dir_paths, subdir_paths):
                        if not subdir_path.startswith(dir_path):
                            redundant_entry = False 

                    if redundant_entry:
                        del reverse_dir_dict[subdir_hash]

    # DISPLAY DUPLICATED FILES AND DIRECTORIES ################################
    
##
#    for path, hash in dir_dict.items():
#        print "%s %s" % (hash, path)
#
#    for path, hash in file_dict.items():
#        print "%s %s" % (hash, path)
#
#    print
#
#    for hash, paths in reverse_dir_dict.items():
#        print "%s %s" % (hash, paths)
#
#    for hash, paths in reverse_file_dict.items():
#        print "%s %s" % (hash, paths)
#
#    print
##

    for hash, paths in reverse_dir_dict.items():
        if len(paths) > 1:
            for path in paths:
                mtime = time.ctime(os.path.getmtime(path))
                print "[%s]   %s" % (mtime, path)
            print

    for hash, paths in reverse_file_dict.items():
        if len(paths) > 1:
            for path in paths:
                mtime = time.ctime(os.path.getmtime(path))
                print "[%s]   %s" % (mtime, path)
            print

# FILE UTILITIES ##############################################################

def md5sum(file_path):
    """Compute hash"""

    hash = hashlib.md5()

    if os.path.isfile(file_path):
        file_descriptor = open(file_path, 'rb')
        try:
            data = file_descriptor.read(CHUNK_SIZE)
            while data:
                hash.update(data)
                data = file_descriptor.read(CHUNK_SIZE)
        finally:
            file_descriptor.close()

    return hash.hexdigest()        # str


def get_default_db_path():
    """Return the default database path."""

    # A cross-platform way to get the current user's home directory
    home_dir = os.path.expanduser("~")
    default_db_filename = ".clonefinder"
    db_path = os.path.join(home_dir, default_db_filename)

    return db_path


if __name__ == '__main__':
    main()

