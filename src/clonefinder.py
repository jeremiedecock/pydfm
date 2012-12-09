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

import dumbdbm

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
    parser.add_argument("--followlinks", "-l", help="follow links", action="store_true")
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
                sys.exit(3)

    print db_path

    # BUILD {PATH:MD5,...} DICTIONARY (WALK THE TREE) #########################

    file_dict = {}   # dict = {path: md5, ...}
    dir_dict = {}    # dict = {path: md5, ...}

    db = None
    if db_path is not None:
        db = dumbdbm.open(db_path, 'c')

    # For each root path specified in command line argmuents
    for path in args.root_paths:
        local_file_dict, local_dir_dict = walk(path, db, args.followlinks)
        file_dict.update(local_file_dict)
        dir_dict.update(local_dir_dict)

    if db_path is not None:
        db.close()

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


    # BUILD {PATH:MD5,...} DICTIONARY (WALK THE TREE) #########################
def walk(root_path, db, follow_links=False):
    """Walk the tree from "root_path" and build the {path:md5,...}
    dictionary"""

    local_file_dict = {}   # dict = {path: md5, ...}
    local_dir_dict = {}    # dict = {path: md5, ...}
    
    # current_dir_path = a string, the path to the directory.
    # dir_names        = a list of the names (strings) of the subdirectories in
    #                    current_dir_path (excluding '.' and '..').
    # file_names       = a list of the names (strings) of the non-directory files
    #                    in current_dir_path.
    for current_dir_path, dir_names, file_names in os.walk(root_path, topdown=False, followlinks=follow_links):

        current_dir_md5 = hashlib.md5()

        # CHILD FILES
        for file_name in file_names:
            file_path = os.path.join(current_dir_path, file_name)
            
            file_mtime = os.path.getmtime(file_path)
            file_size = os.path.getsize(file_path)
            file_md5 = None

            if db != None:
                if file_path in db:
                    #db_file_mtime, db_file_size, db_file_md5 = db[file_path]
                    db_file_mtime, db_file_size, db_file_md5 = db[file_path].split()
                    if file_mtime == db_file_mtime and file_size == db_file_size:
                        # The file is known and hasn't changed since the last walk => don't compute the MD5, use the one in db.
                        file_md5 = db_file_md5

            if file_md5 is None:
                file_md5 = md5sum(file_path)
                if db != None:
                    #db[file_path] = (file_mtime, file_size, file_md5)
                    db[file_path] = "{0} {1} {2}".format(file_mtime, file_size, file_md5)

            local_file_dict[file_path] = file_md5

            current_dir_md5.update(file_md5)

        # CHILD DIRECTORIES
        for dir_name in dir_names:
            dir_path = os.path.join(current_dir_path, dir_name)

            try:
                dir_md5 = local_dir_dict[dir_path]
                current_dir_md5.update(dir_md5)
            except KeyError:
                # "local_dir_dict[dir_path]" should exists as we are doing a bottom-up tree walk
                print 'Internal error. Check whether or not "topdown" argument is set to "False" in os.walk function call.'
                sys.exit(4)

        # CURRENT DIRECTORY
        local_dir_dict[current_dir_path] = current_dir_md5.hexdigest()

        return local_file_dict, local_dir_dict


if __name__ == '__main__':
    main()

