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
The clonefinder core module.
"""

__all__ = ['run',
           'reverse_dictionary',
           'remove_unique_items',
           'remove_redundant_entries',
           'compute_directory_likeness',
           'walk']

import collections
import dbm.dumb      # TODO
import hashlib       # TODO
import itertools
import os
import warnings

from clonefinder.file_hash import md5sum
from clonefinder.database import get_default_db_path, print_db, clear_db

LIKENESS_THRESHOLD = 0

def run(root_paths, db_path=None):

    # BUILD {PATH:MD5,...} DICTIONARY (WALK THE TREE) #########################

    file_dict = {}   # dict = {path: md5, ...}
    dir_dict = {}    # dict = {path: md5, ...}

    db = None
    if db_path is not None:
        db = dbm.dumb.open(db_path, 'c')

    # For each root path specified in command line argmuents
    for path in root_paths:
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

    # COMPUTE DIRECTORY LIKENESS ##############################################

    directory_likeness_dict = compute_directory_likeness(reversed_file_dict,
                                                         file_dict,
                                                         dir_dict)

    # DISPLAY DUPLICATED FILES AND DIRECTORIES ################################

    # DIRECTORIES
    num_cloned_dir = len(reversed_dir_dict)
    if num_cloned_dir > 0:
        suffix = "Y" if num_cloned_dir == 1 else "IES"
        print("*** {0} CLONED DIRECTOR{1} ***\n".format(num_cloned_dir, suffix))
        for md5, paths in list(reversed_dir_dict.items()):
            for path in paths:
                print(path)
            print()
    else:
        print("*** NO CLONED DIRECTORY ***\n")

    # DIRECTORIES LIKENESS
    directory_likeness_list = [item for item in list(directory_likeness_dict.items()) if LIKENESS_THRESHOLD < item[1] < 100]
    directory_likeness_list.sort(key=lambda x: x[1], reverse=True)
    if len(directory_likeness_list) > 0:
        print("*** DIRECTORIES LIKENESS ***")
        print()
        for path_pair, likeness in directory_likeness_list:
            assert len(path_pair) == 2
            print("{0}%".format(likeness))
            print(path_pair[0])
            print(path_pair[1])
            print()

    # FILES
    num_cloned_files = len(reversed_file_dict)
    if num_cloned_files > 0:
        suffix = "" if num_cloned_files == 1 else "S"
        print("*** {0} CLONED FILE{1} ***\n".format(num_cloned_files, suffix))
        for md5, paths in list(reversed_file_dict.items()):
            for path in paths:
                print(path)
            print()
    else:
        print("*** NO CLONED FILE ***\n")


# TOOLS

def reverse_dictionary(dictionary):
    """Build a reversed dictionary of the one given in argument
    (i.e. keys become values and values become keys).

    reverse_dictionary({key1:val1, key2:val1, key3:val2})
    returns {val1:[key1, key2], val2:[key3]}."""

    reversed_dictionary = {}

    for key, value in list(dictionary.items()):
        if value not in reversed_dictionary:
            reversed_dictionary[value] = []
        reversed_dictionary[value].append(key)

    return reversed_dictionary


def remove_unique_items(reversed_dict):
    """Remove non-cloned items in the reversed dictionary given in argument."""

    clone_reversed_dict = {md5: paths for md5, paths in list(reversed_dict.items()) if len(paths) > 1}

    return clone_reversed_dict


def remove_redundant_entries(reversed_dict, dir_dict):
    r"""Supprime les fichiers redondants avec les répertoires affichés comme
    clonés...

    reverse_dict = {md5: [path1, path2, ...], ...}

    Pour chaque item du dictionnaire, si le répertoire père de tous les paths
    ont tous le même MD5 et au moins un chemin différent, alors le fichier peut
    être supprimé.

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
      D/2 seront affiché comme clonés mais pourtant seront seul dans la liste
      des chemins...

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

    EXEMPLE3:

        A      B¹     B²
       / \    /|\    /|\
      1¹  1² 1¹1²2  1¹1²2
                 X      X

      AVANT:

      {3283298720787ba7:[B¹, B²],
       769726937697abff:[A/1¹, A/1², B¹/1¹, B¹/1², B²/1¹, B²/1²],
       9fbba679127aa8cb:[B¹/2, B²/2]}

      APRÈS:

      {3283298720787ba7:[B¹, B²],
       769726937697abff:[A/1¹, A/1², B¹/1¹, B¹/1², B²/1¹, B²/1²]}
    """

    keys_to_remove = []

    # reverse_dict = {md5: [path1, path2, ...], ...}
    for md5, path_list in list(reversed_dict.items()):
        parent_md5_set = set()
        parent_path_set = set()

        assert len(path_list) > 1, str(path_list)

        for path in path_list:
            parent_path = os.path.dirname(path)
            if parent_path in dir_dict:
                parent_md5 = dir_dict[parent_path]
                parent_md5_set.add(parent_md5)
                parent_path_set.add(parent_path)
            else:
                # Root directories don't have parents in parent_path
                warnings.warn("root directory ? " + path) # TODO: check

        # if all parents have the same content and if there are at least
        # 2 parents
        if len(parent_md5_set) == 1 and len(parent_path_set) > 1:
            keys_to_remove.append(md5)

    for key in keys_to_remove:
        #print "remove", key
        del reversed_dict[key]


def compute_directory_likeness(reversed_file_dict, file_dict, dir_dict):
    """Compute directories similarity

    reverse_file_dict = {md5: [path1, path2, ...], ...}
    file_dict = {path: md5, ...}
    dir_dict = {path: md5, ...}

    1. construit l'ensemble des répertoires contenant des fichiers clonés

    2. construit la liste des combinaisons possibles de ces répertoires avec
       itertools.combinations():

          [DIR1, DIR2, DIR3] -> ((DIR1,DIR2), (DIR1,DIR3), (DIR2,DIR3))

                                      1 2 3
                                    1 . x x
                                    2 . . x
                                    3 . . .

    3. crée un dictionnaire ayant comme clé les couples construits dans 2.
       et comme valeur le pourcentage de fichiers clonnées dans le couple
       (par rapport à l'union de tous les fichiers du couple):

          {(DIR1, DIR2): PERCENT, ...}

       avec PERCENT = #(DIR1 ∩ DIR2) / #(DIR1 ∪ DIR2) * 100.

    4. retourne ce dictionnaire
    """

    # Construit l'ensemble des répertoires contenant des fichiers clonés
    dir_set = set()
    for md5, paths in list(reversed_file_dict.items()):
        for path in paths:
            dir_set.add(os.path.dirname(path))

    # Make file_dir_dict the "union" of file_dict and dir_dict
    file_dir_dict = file_dict.copy()
    file_dir_dict.update(dir_dict)
    assert len(file_dir_dict) == len(file_dict) + len(dir_dict)

    # Construit la liste des combinaisons possibles de ces répertoires
    # et le dictionnaire {(DIR1, DIR2): PERCENT, ...}
    directory_likeness_dict = {}
    for path_pair in itertools.combinations(dir_set, 2):

        file_path_list_1 = [os.path.join(path_pair[0], file_name) for file_name in os.listdir(path_pair[0])]
        file_path_list_2 = [os.path.join(path_pair[1], file_name) for file_name in os.listdir(path_pair[1])]

        file_md5_list_1 = [file_dir_dict[file_path] for file_path in file_path_list_1]
        file_md5_list_2 = [file_dir_dict[file_path] for file_path in file_path_list_2]

        # On utilise des multisets (collections.Counter en Python) plutot que
        # des sets ou des frozensets car il se peut qu'un meme MD5 soit present
        # plusieurs fois dans le meme repertoire.
        file_md5_multiset_1 = collections.Counter(file_md5_list_1)
        file_md5_multiset_2 = collections.Counter(file_md5_list_2)

        inter_file_multiset = file_md5_multiset_1 & file_md5_multiset_2
        union_file_multiset = file_md5_multiset_1 | file_md5_multiset_2

        likeness = 100. * sum(inter_file_multiset.values()) / sum(union_file_multiset.values())

        directory_likeness_dict[path_pair] = likeness

    return directory_likeness_dict


# BUILD {PATH:MD5,...} DICTIONARY (WALK THE TREE) #############################

def walk(root_path, db):
    """Walk the tree starting from "root_path" and build the {path:md5,...}
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
                            # The file is known and hasn't changed since the
                            # last walk => don't compute the MD5, use the one
                            # in db.
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
            current_dir_md5_generator.update(bytes(item, 'utf-8'))  # TODO
        local_dir_dict[current_dir_path] = current_dir_md5_generator.hexdigest()

    return local_file_dict, local_dir_dict

