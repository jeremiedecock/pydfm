#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2010,2011,2012,2013 Jérémie DECOCK (http://www.jdhp.org)

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
import argparse
import hashlib
import warnings

import dumbdbm

VERSION = "2.0"
COPYING = '''Copyright (c) 2010,2011,2012,2013 Jeremie DECOCK (http://www.jdhp.org)
This is free software; see the source for copying conditions.
There is NO warranty; not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.'''

CHUNK_SIZE = 2**12

def custom_formatwarning(message, category, filename, lineno, line=""):
    """Ignore everything except the message."""
    return "Warning: " + str(message) + "\n"

def main():
    """Main function"""

    warnings.formatwarning = custom_formatwarning

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
    print

    # BUILD {PATH:MD5,...} DICTIONARY (WALK THE TREE) #########################

    file_dict = {}   # dict = {path: md5, ...}
    dir_dict = {}    # dict = {path: md5, ...}

    db = None
    if db_path is not None:
        db = dumbdbm.open(db_path, 'c')

    # For each root path specified in command line argmuents
    for path in args.root_paths:
        local_file_dict, local_dir_dict = walk(path, db)
        file_dict.update(local_file_dict)
        dir_dict.update(local_dir_dict)

    if db_path is not None:
        db.close()

    # BUILD REVERSE DICTIONNARY ###############################################

    # reverse_dict = {md5: [path1, path2, ...], ...}
    reversed_file_dict = reverse_dictionary(file_dict)
    reversed_dir_dict = reverse_dictionary(dir_dict)

    # REMOVE UNIQUE ITEMS #####################################################

    reversed_file_dict = remove_unique_items(reversed_file_dict)
    reversed_dir_dict = remove_unique_items(reversed_dir_dict)

    # REMOVE REDUNDANT ENTRIES ################################################

    remove_redundant_entries(reversed_file_dict, dir_dict)
    remove_redundant_entries(reversed_dir_dict, dir_dict)

    # DISPLAY DUPLICATED FILES AND DIRECTORIES ################################

    # DIRECTORIES
    num_cloned_dir = len(reversed_dir_dict)
    if num_cloned_dir > 0:
        print "*** {0} CLONED DIRECTOR{1} ***".format(num_cloned_dir, ("Y" if num_cloned_dir==1 else "IES"))
        print
        for md5, paths in reversed_dir_dict.items():
            for path in paths:
                print path
            print
    else:
        print "*** NO CLONED DIRECTORY ***"
        print

    # FILES
    num_cloned_files = len(reversed_file_dict)
    if num_cloned_files > 0:
        print "*** {0} CLONED FILE{1} ***".format(num_cloned_files, ("" if num_cloned_files==1 else "S"))
        print
        for md5, paths in reversed_file_dict.items():
            for path in paths:
                print path
            print
    else:
        print "*** NO CLONED FILE ***"
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
        #db = dumbdbm.open(db_path, 'n')  # TODO: it doesn't work...
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


def remove_unique_items(reversed_dict):
    """Remove non-cloned items in the reversed dictionary given in argument."""

    clone_reversed_dict = {md5: paths for md5, paths in reversed_dict.items() if len(paths)>1}

    return clone_reversed_dict


def remove_redundant_entries(reversed_dict, dir_dict):
    """Supprime les fichiers redondants avec les répertoires affichés comme
    clonés...

    Pour chaque item du dictionnaire, si le répertoire père de tous les paths
    ont tous le même MD5, alors le fichier peut être supprimé.

    EXEMPLE1:

        A      B      C    
        |      |      |    
        D      E      E    
       / \    /|\    /|\   
      1   2  1 2 3  1 2 3  
                 X      X

      AVANT:

      {3283298720787ba7:[B/E, C/E],
       769726937697abff:[A/D/1, B/E/1, C/E/1],
       6bffe3890aa890be:[A/D/2, B/E/2, C/E/2],
       9fbba679127aa8cb:[B/E/3, C/E/3]}

      APRÈS:

      {3283298720787ba7:[B/E, C/E],
       769726937697abff:[A/D/1, B/E/1, C/E/1],
       6bffe3890aa890be:[A/D/2, B/E/2, C/E/2]}
    
      A/3 doit être retiré du dictinnaire mais pas E/1 et E/2 car sinon, D/1 et
      D/2 seront affiché comme clonés mais pourtant seront seul dans la liste des
      chemins...

    EXEMPLE2 (TODO):

        A      B      C      H   
        |      |      |      |   
        D      E      E      D   
       / \    /|\    /|\    / \  
      1   2  1 2 3  1 2 3  1   2 
      X   X  X X X  X X X  X   X 

      AVANT:

      {3283298720787ba7:[B/E, C/E],
       682763179aab2763:[A/D, H/D],
       769726937697abff:[A/D/1, B/E/1, C/E/1, H/D/1],
       6bffe3890aa890be:[A/D/2, B/E/2, C/E/2, H/D/2],
       9fbba679127aa8cb:[B/E/3, C/E/3]}

      APRÈS:

      {3283298720787ba7:[B/E, C/E],
       682763179aab2763:[A/D, H/D]}

    """

    keys_to_remove = []

    for md5, path_list in reversed_dict.items():
        parent_md5_set = set()

        assert len(path_list) > 1, str(path_list)

        for path in path_list:
            parent_path = os.path.dirname(path)
            if parent_path in dir_dict:
                parent_md5 = dir_dict[parent_path]
                parent_md5_set.add(parent_md5)
            else:
                # Root directories don't have parents in parent_path
                warnings.warn("root directory ? " + path) # TODO: check

        if len(parent_md5_set) == 1:
            keys_to_remove.append(md5)

    for key in keys_to_remove:
        #print "remove", key
        del reversed_dict[key]


# BUILD {PATH:MD5,...} DICTIONARY (WALK THE TREE) #########################

def walk(root_path, db):
    """Walk the tree from "root_path" and build the {path:md5,...}
    dictionary"""

    local_file_dict = {}   # dict = {path: md5, ...}
    local_dir_dict = {}    # dict = {path: md5, ...}
    
    # current_dir_path = a string, the path to the directory.
    # dir_names        = a list of the names (strings) of the subdirectories in
    #                    current_dir_path (excluding '.' and '..').
    # file_names       = a list of the names (strings) of the non-directory files
    #                    in current_dir_path.
    for current_dir_path, dir_names, file_names in os.walk(root_path, topdown=False, followlinks=False):

        # ABSOLUTE PATH OF current_dir_path
        current_dir_path = os.path.abspath(current_dir_path)

        # MAKE THE MD5 LIST OF CURRENT_DIR'S CONTENT (REQUIRED TO COMPUTE
        # CURRENT_DIR'S MD5)
        current_dir_md5_list = []

        # CHILD FILES
        for file_name in file_names:
            file_path = os.path.join(current_dir_path, file_name)
            
            if not os.path.islink(file_path):
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

                current_dir_md5_list.append(file_md5)
#            else:
#                warnings.warn("ignore link " + file_path, UserWarning)

        # CHILD DIRECTORIES
        for dir_name in dir_names:
            dir_path = os.path.join(current_dir_path, dir_name)

            if not os.path.islink(dir_path):
                try:
                    dir_md5 = local_dir_dict[dir_path]
                    current_dir_md5_list.append(dir_md5)
                except KeyError:
                    ## "local_dir_dict[dir_path]" should exists as we are doing a bottom-up tree walk
                    #print 'Internal error. Check whether or not "topdown" argument is set to "False" in os.walk function call.'
                    #print dir_path, "key doesn't exist in \"local_dir_dict\" dictionary."
                    #sys.exit(4)
                    warnings.warn("can't access " + dir_path, UserWarning)
#            else:
#                warnings.warn("ignore link " + dir_path, UserWarning)

        # CURRENT_DIRECTORY'S MD5
        current_dir_md5_generator = hashlib.md5()

        # current_dir_md5_list have to be sorted because even for an identical
        # set of items, different order implies different MD5
        current_dir_md5_list.sort()

        for item in current_dir_md5_list:
            current_dir_md5_generator.update(item)
        local_dir_dict[current_dir_path] = current_dir_md5_generator.hexdigest()

    return local_file_dict, local_dir_dict


if __name__ == '__main__':
    main()

