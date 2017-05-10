# TODO

## Version 3.0

- [ ] Fix the bug on Latin* characters in file names
- [ ] Add a feature: say if 2 directories are strictly identical (MD5 and
      filenames), if not, show differences
- [ ] Add a feature: say if 2 directories have no file in common (disjoint MD5
      sets), if not, show common files
- [ ] Update the README file: explain the main features, explain how it works
      (use tree pictures, ...), explain why the duplicate file search is not
      "trivial" at all (md5 not filename, minimal list, likelyhood similitudes,
      ...), ...
- [ ] Clean, add docstrings, test, ...
- [ ] Add a setup.py file
- [ ] Introduce a special consideration for empty files : remove them from the
      "cloned files list" and display them in an "empty files list"
- [ ] Create a Debian package
- [ ] Ensure it works on Windows and MacOSX platforms + add installation
      instructions for Windows and MacOSX in the README file
- [ ] How to manage unreadable ("chmod a-r") files or directories ? Two identical
      directories containing at least one unreadable file should be considered as
      cloned anyway or not (or should require a special display in the report) ?

## Version 3.1

- [ ] Add a graphical user interface (GTK+3)
    - [ ] Select directories
    - [ ] Progress bar (2 pass scan)
    - [ ] Result in a TreeView
    - [ ] Actions (remove a file, ...)
    - ...
- [ ] Update the README file: new instructions for the GUI, user guide, ...

- [ ] Read http://www.techsupportalert.com/best-free-duplicate-file-detector.htm
