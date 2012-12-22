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

    class RootPathsAction(argparse.Action):
        """Argparse's action class for 'root_paths' arguments."""
        def __call__(self, parser, args, values, option = None):
            if not args.printdb and not args.cleardb and  len(values) == 0:
                parser.error("too few arguments")
            else:
                args.root_paths = values

    parser = argparse.ArgumentParser(description='Find duplicated files and directories.')

    parser.add_argument("--db", "-d", help="database path", metavar="STRING")
    parser.add_argument("--nodb", "-n", help="don't use database file", action="store_true")
    parser.add_argument("--printdb", "-p", help="print the database content and exit", action="store_true")
    parser.add_argument("--cleardb", "-c", help="remove the database content and exit", action="store_true")
    parser.add_argument("--followlinks", "-l", help="follow links", action="store_true")
    parser.add_argument("--version", "-v", action="version", version="%(prog)s " + VERSION)
    parser.add_argument("root_paths", nargs="*", metavar="DIRECTORY", help="root directory", action=RootPathsAction)

    args = parser.parse_args()

    # SET DB_PATH
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

    # PRINT_DB AND EXIT IF REQUESTED
    if args.printdb:
        print_db(db_path)
        sys.exit(0)

    # CLEAR_DB AND EXIT IF REQUESTED
    if args.cleardb:
        clear_db(db_path)
        sys.exit(0)

    # CHECK ROOT_PATHS
    for path in args.root_paths:
        if not os.path.isdir(path):
            print "ERROR: {0} is not a directory.".format(path)
            print parser.format_usage(),
            sys.exit(2)

    print "Using", db_path, "database"

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

    # reverse_dict = {md5: [path1, path2, ...], ...}
    reversed_file_dict = reverse_dictionary(file_dict)
    reversed_dir_dict = reverse_dictionary(dir_dict)

    # REMOVE REDUNDANT ENTRIES ################################################

    for dir_hash, dir_paths in reversed_dir_dict.items():
        if len(dir_paths) > 1:
            for file_hash, file_paths in reversed_file_dict.items():
                if len(file_paths) == len(dir_paths):
                    file_paths.sort()
                    dir_paths.sort()

                    redundant_entry = True
                    for dir_path, file_path in zip(dir_paths, file_paths):
                        if not file_path.startswith(dir_path):
                            redundant_entry = False 

                    if redundant_entry:
                        del reversed_file_dict[file_hash]
            for subdir_hash, subdir_paths in reversed_dir_dict.items():
                if (len(subdir_paths) == len(dir_paths)) and (subdir_paths is not dir_paths):
                    subdir_paths.sort()
                    dir_paths.sort()

                    redundant_entry = True
                    for dir_path, subdir_path in zip(dir_paths, subdir_paths):
                        if not subdir_path.startswith(dir_path):
                            redundant_entry = False 

                    if redundant_entry:
                        del reversed_dir_dict[subdir_hash]

    # DISPLAY DUPLICATED FILES AND DIRECTORIES ################################

    if len(reversed_dir_dict) > 0:      # TODO: prune reversed_dir_dict before
        print "* CLONED DIRECTORIES:"
        for md5, paths in reversed_dir_dict.items():
            if len(paths) > 1:
                for path in paths:
                    mtime = time.ctime(os.path.getmtime(path))  # TODO: don't fetch mtime again...
                    print "[%s]   %s" % (mtime, path)
                print

    if len(reversed_file_dict) > 0:      # TODO: prune reversed_file_dict before
        print "* CLONED FILES:"
        for md5, paths in reversed_file_dict.items():
            if len(paths) > 1:
                for path in paths:
                    mtime = time.ctime(os.path.getmtime(path))  # TODO: don't fetch mtime again...
                    print "[%s]   %s" % (mtime, path)
                print


# FILE UTILITIES ##############################################################

def md5sum(file_path):
    """Compute md5"""

    md5_generator = hashlib.md5()

    if os.path.isfile(file_path):
        file_descriptor = open(file_path, 'rb')
        try:
            data = file_descriptor.read(CHUNK_SIZE)
            while data:
                md5_generator.update(data)
                data = file_descriptor.read(CHUNK_SIZE)
        finally:
            file_descriptor.close()

    return md5_generator.hexdigest()        # str


# DB UTILITIES ################################################################

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
        db = dumbdbm.open(db_path, 'c')

        if len(db) == 0:
            print "Empty database."
        else:
            for file_path, file_attributes in db.items():
                file_mtime, file_size, file_md5 = file_attributes.split()
                print "{path} {mtime} {size} {md5}".format(path=file_path, mtime=file_mtime, size=file_size, md5=file_md5)
            print len(db), "files are recorded in", db_path

        db.close()
    else:
        print "No database."


def clear_db(db_path):
    """Remove the database content."""

    if db_path is not None:
        print "Clear ", db_path
        db = dumbdbm.open(db_path, 'c')
        db.clear()
        db.close()
    else:
        print "No database."


# TOOLS

def reverse_dictionary(dictionary):
    """Build a reversed dictionary of the one given in argument
    (i.e. keys become values and values become keys).

    reverse_dictionary({key1:val1, key2:val1, key3:val2})
    returns {val1:[key1, key2], val2:[key3]}."""

    reversed_dictionary = {}

    for key, value in dictionary.items():
        if not reversed_dictionary.has_key(value):
            reversed_dictionary[value] = []
        reversed_dictionary[value].append(key)

    return reversed_dictionary


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

        # ABSOLUTE PATH OF current_dir_path
        current_dir_path = os.path.abspath(current_dir_path)

        # MAKE THE MD5 CURRENT_DIR GENERATOR
        current_dir_md5_generator = hashlib.md5()

        # CHILD FILES
        for file_name in file_names:
            file_path = os.path.join(current_dir_path, file_name)
            
            file_mtime = os.path.getmtime(file_path)
            file_size = os.path.getsize(file_path)
            file_md5 = None

            if db is not None:
                if file_path in db:
                    db_file_mtime, db_file_size, db_file_md5 = db[file_path].split()
                    if file_mtime == db_file_mtime and file_size == db_file_size:
                        # The file is known and hasn't changed since the last walk => don't compute the MD5, use the one in db.
                        file_md5 = db_file_md5

            if file_md5 is None:
                file_md5 = md5sum(file_path)
                if db is not None:
                    db[file_path] = "{0} {1} {2}".format(file_mtime, file_size, file_md5)

            local_file_dict[file_path] = file_md5

            current_dir_md5_generator.update(file_md5)

        # CHILD DIRECTORIES
        for dir_name in dir_names:
            dir_path = os.path.join(current_dir_path, dir_name)

            try:
                dir_md5 = local_dir_dict[dir_path]
                current_dir_md5_generator.update(dir_md5)
            except KeyError:
                # "local_dir_dict[dir_path]" should exists as we are doing a bottom-up tree walk
                print 'Internal error. Check whether or not "topdown" argument is set to "False" in os.walk function call.'
                sys.exit(4)

        # CURRENT DIRECTORY
        local_dir_dict[current_dir_path] = current_dir_md5_generator.hexdigest()

    return local_file_dict, local_dir_dict


if __name__ == '__main__':
    main()

