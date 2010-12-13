#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2010 Jérémie DECOCK (http://www.jdhp.org)


# http://www.techsupportalert.com/best-free-duplicate-file-detector.htm

import os
import sys
import getopt
import hashlib

CHUNK_SIZE = 2**12

def usage():
    """Print help message"""

    print '''Usage : ./clonefinder [-q] [-h] DIRECTORY
    
    Find identical files in PATH.

    -q, --quiet
        ...

    -h, --help
        display this help and exit
    '''

def main():
    """Main function"""
    # Utiliser argparse à partir de python 2.7 (optparse is deprecated)
    
    # Parse options ###########################################################
    path = None
    quiet = False

    try:
        opts, args = getopt.getopt(sys.argv[1:],
                     'qh',
                     ["quiet", "help"])
    except getopt.GetoptError, err:
        # will print something like "option -x not recognized"
        print str(err) 
        usage()
        sys.exit(1)
 
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit(0)
        elif o in ("-q", "--quiet"):
            quiet = True
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

    if not quiet:
        print "scanning directory...",
        sys.stdout.flush()

    tree = []
    for directory in os.walk(path, topdown=False):
        tree.append(directory)

    if not quiet:
        print "done."
        
    number_of_files = 0
    for root, dirs, files in tree:
        number_of_files += len(files)

    if not quiet:
        print "%d files found." % number_of_files
        print

    # Compute checksums #######################################################

    dict = {}

    # cf. os.walk    (os.path.walk() is deprecated)
    file_counter = 0
    for root, dirs, files in tree:
        #root_digest = hashlib.md5()    # md5() is deprecated, use hashlib.md5() instead

        for name in files:
            file_counter += 1
            if not quiet:
                print "\r",
                print "processing file %d" % (file_counter),
                print "of %d" % (number_of_files),
                print "(%d%%)" % (float(file_counter)/float(number_of_files)*100.),
                sys.stdout.flush()

            file_digest = digest(os.path.join(root, name))
            #root_digest.update(file_digest)
            
            if not dict.has_key(file_digest):
                dict[file_digest] = []
            dict[file_digest].append(os.path.join(root, name))

        for name in dirs:
            #root_digest.update(dir_digest)

        #root_digest.hexdigest()        # text

    if not quiet:
        print
        print

    cpt = 0
    for key, values in dict.items():
        if len(values) > 1:
            cpt += 1
            if cpt > 1:
                print
            if not quiet:
                print "* File %d :" % cpt
            for value in values:
                print "%s" % value


#import os
#from os.path import join, getsize
#for root, dirs, files in os.walk('python/Lib/email'):
#    print root, "consumes",
#    print sum(getsize(join(root, name)) for name in files),
#    print "bytes in", len(files), "non-directory files"
#    if 'CVS' in dirs:
#        dirs.remove('CVS')  # don't visit CVS directories


#def get_tree(path):
#    # cf. os.path
#    pass

def digest(file_path):
    #you could say
    #print md5.new(file('foo.exe').read()).hexdigest()
    #but that means reading the whole file into memory at once. If the
    #file is very large, that could thrash or fail.

    #Break the file into 128-byte chunks and feed them to MD5 consecutively using update().
    #This takes advantage of the fact that MD5 has 128-byte digest blocks. Basically, when MD5 digest()s the file, this is exactly what it is doing.
    #If you make sure you free the memory on each iteration (i.e. not read the entire file to memory), this shall take no more than 128 bytes of memory.
    #One example is to read the chunks like so:
    #f = open(fileName)
    #while not endOfFile:
    #    f.read(128)
    #edited Jul 15 '09 at 14:40
    #answered Jul 15 '09 at 12:55
    #Yuval A
    #    
    #Python is garbage-collected, so there's (usually) not really a need to worry about memory. Unless you explicitly keep around references to all the strings you read from the file, python will free and/or reuse as it sees fit. – Kjetil Jorgensen Jul 15 '09 at 13:18
    #1    
    #    
    #@kjeitikor: If you read the entire file into e.g. a Python string, then Python won't have much of a choice. That's why "worrying" about memory makes total sense in this case, where the choice to read it in chunks must be made by the programmer. – unwind Jul 15 '09 at 14:43
    #2    
    #    
    #You can just as effectively use a block size of any multiple of 128 (say 8192, 32768, etc.) and that will be much faster than reading 128 bytes at a time. – jmanning2k Jul 15 '09 at 15:09
    #2    
    #    
    #Thanks jmanning2k for this important note, a test on 184MB file takes (0m9.230s, 0m2.547s, 0m2.429s) using (128, 8192, 32768), I will use 8192 as the higher value gives non-noticeable affect. – JustRegisterMe Jul 17 '09 at 19:33

    md5 = hashlib.md5()    # md5() is deprecated, use hashlib.md5() instead

    if os.path.isfile(file_path):
        file_descriptor = open(file_path, 'rb')
        try:
            data = file_descriptor.read(CHUNK_SIZE)
            while data:
                md5.update(data)
                data = file_descriptor.read(CHUNK_SIZE)
        finally:
            file_descriptor.close()

    return md5.hexdigest()        # text
    #return md5.digest()          # bin


    #if you care about more pythonic (no 'while True') way of reading the file check this code:
    #
    #import hashlib
    #md5 = hashlib.md5()
    #with open('myfile.txt','rb') as f: 
    #    for chunk in iter(lambda: f.read(8192), ''): 
    #         md5.update(chunk)
    #return md5.digset()

if __name__ == '__main__':
    main()

