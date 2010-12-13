#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import getopt

# stack = [[dir, [dir_content], [md5_dir_content]],
#          ...
#          [file],
#          ...
#         ]

stack = []
md5_dict = {}

def usage():
    """Print help message"""

    print '''Usage : ./clonefinder [-h] DIRECTORY
    
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
        path = args[0]
    except IndexError:
        usage()
        sys.exit(1)

    if not os.path.isdir(path):
        usage()
        sys.exit(2)

    # Build directory tree ####################################################

    depth_first_search(path)

def depth_first_search(root):
    push(root)
    
    while len(stack) > 0:
        print stack

        node = stack[-1]

        if len(node) == 1:                         # node is a file
            file_hash(node)
            pop()
        elif len(node) == 3:                       # node is a directory
            if len(node[1]) == 0:                  # has nothing to explore
                dir_hash(node)
                pop()
            else:                                  # has content to explore
                push(os.path.join(node[0], node[1][0]))
                del node[1][0]

def push(node):
    if os.path.isfile(node) and not os.path.islink(node):
        stack.append([node])
    elif os.path.isdir(node) and not os.path.islink(node):
        node_content = os.listdir(node)
        stack.append([node, node_content, []])

def pop():
    del stack[-1]

def file_hash(node):
    pass

def dir_hash(node):
    pass

if __name__ == '__main__':
    main()

