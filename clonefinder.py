#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2010 Jérémie DECOCK (http://www.jdhp.org)


# http://www.techsupportalert.com/best-free-duplicate-file-detector.htm


import os
import sys
import time
import getopt
import hashlib

CHUNK_SIZE = 2**12

def usage():
    """Print help message"""

    print '''Usage : ./clonefinder [-h] DIRECTORY [DIRECTORY, ...]
    
    Find identical files in PATH.

    -h, --help
        display this help and exit
    '''

def main():
    """Main function"""
    # Utiliser argparse à partir de python 2.7 (optparse is deprecated)
    
    # Parse options ###########################################################
    path = None

    try:
        opts, args = getopt.getopt(sys.argv[1:],
                     'h',
                     ["help"])
    except getopt.GetoptError, err:
        # will print something like "option -x not recognized"
        print str(err) 
        usage()
        sys.exit(1)
 
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit(0)
        else:
            assert False, "unhandled option"

    try:
        root_paths = args
    except IndexError:
        usage()
        sys.exit(1)

    for path in root_paths:
        if not os.path.isdir(path):
            usage()
            sys.exit(2)

    # Compute hashs ###########################################################

    # dict = {path: hash, ...}
    file_dict = {}
    dir_dict = {}

    for path in root_paths:
        for root, dirs, files in os.walk(path, topdown=False):
            root_digest = hashlib.md5()

            for name in files:
                file_path = os.path.join(root, name)
                file_digest = digest(file_path)
                file_dict[file_path] = file_digest
                
                root_digest.update(file_digest)

            for name in dirs:
                dir_path = os.path.join(root, name)
                root_digest.update(dir_dict[dir_path])

            dir_dict[root] = root_digest.hexdigest()

    # Build reverse dictionnary ###############################################

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

    # Remove redundant entries ################################################

#    for dir_hash, dir_paths in reverse_dir_dict.items():
#        if len(dir_paths) > 1:
#            for file_hash, file_paths in reverse_file_dict.items():
#                if len(file_paths) == len(dir_paths):
#                    file_paths.sort()
#                    dir_paths.sort()
#
#                    redundant_entry = True
#                    for dir_path, file_path in zip(dir_paths, file_paths):
#                        if not file_path.startswith(dir_path):
#                            redundant_entry = False 
#
#                    if redundant_entry:
#                        del reverse_file_dict[file_hash]
#            for subdir_hash, subdir_paths in reverse_dir_dict.items():
#                if len(subdir_paths) == len(dir_paths):
#                    subdir_paths.sort()
#                    dir_paths.sort()
#
#                    redundant_entry = True
#                    for dir_path, subdir_path in zip(dir_paths, subdir_paths):
#                        if not subdir_path.startswith(dir_path):
#                            redundant_entry = False 
#
#                    if redundant_entry:
#                        del reverse_dir_dict[subdir_hash]

    # Display duplicated files and directories ################################
    
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


def digest(file_path):
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

    return hash.hexdigest()        # text

if __name__ == '__main__':
    main()

