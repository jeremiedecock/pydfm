=======================
PyDuplicateFileManager_
=======================

Copyright (c) 2010,2011,2015 Jérémie DECOCK (http://www.jdhp.org)


* Web site: http://www.jdhp.org/projects_en.html#pydfm
* Online documentation: http://pydfm.readthedocs.org
* Source code: https://github.com/jeremiedecock/pydfm
* Issue tracker: https://github.com/jeremiedecock/pydfm/issues
* PyDuplicateFileManager on PyPI: https://pypi.python.org/pypi/pydfm

Note:

    This project is still in beta stage, so the API is not finalized yet.


Description
===========

PyDuplicateFileManager finds duplicated files and directories.

PyDuplicateFileManager is written in Python and released under the MIT license.


Dependencies
============

PyDuplicateFileManager is tested to work with Python 3.4 under Gnu/Linux Debian
8 and Windows 7.
It should also work with Python 3.X under recent Gnu/Linux and Windows systems.
It hasn't been tested (yet) on MacOSX and BSD systems.


.. _install:

Installation
============

Gnu/Linux
---------

You can install, upgrade, uninstall PyDuplicateFileManager with these commands
(in a terminal)::

    pip install --pre pydfm
    pip install --upgrade pydfm
    pip uninstall pydfm

Or, if you have downloaded the PyDuplicateFileManager source code::

    python3 setup.py install

.. There's also a package for Debian/Ubuntu::
.. 
..     sudo apt-get install pydfm

Windows
-------

Note:

    The following installation procedure has been tested to work with Python
    3.4 under Windows 7.
    It should also work with recent Windows systems.

You can install, upgrade, uninstall PyDuplicateFileManager with these commands
(in a `command prompt`_)::

    py -m pip install --pre pydfm
    py -m pip install --upgrade pydfm
    py -m pip uninstall pydfm

Or, if you have downloaded the PyDuplicateFileManager source code::

    py setup.py install

.. MacOSX
.. -------
.. 
.. Note:
.. 
..     The following installation procedure has been tested to work with Python
..     3.4 under MacOSX 10.6 (*Snow Leopard*).
..     It should also work with recent MacOSX systems.
.. 
.. You can install, upgrade, uninstall PyDuplicateFileManager with these
.. commands (in a terminal)::
.. 
..     pip install --pre pydfm
..     pip install --upgrade pydfm
..     pip uninstall pydfm
.. 
.. Or, if you have downloaded the PyDuplicateFileManager source code::
.. 
..     python3 setup.py install


Documentation
=============

.. PyDuplicateFileManager documentation is available on the following page:
.. 
..     http://pydfm.rtfd.org/

- Online Documentation: http://pydfm.readthedocs.org
- API Documentation: http://pydfm.readthedocs.org/en/latest/api.html


Example usage
=============

TODO...


Bug reports
===========

To search for bugs or report them, please use the PyDuplicateFileManager Bug
Tracker at:

    https://github.com/jeremiedecock/pydfm/issues


License
=======

PyDuplicateFileManager is provided under the terms and conditions of the
`MIT License`.

.. _PyDuplicateFileManager: http://www.jdhp.org/projects_en.html#pydfm
.. _MIT License: http://opensource.org/licenses/MIT
.. _command prompt: https://en.wikipedia.org/wiki/Cmd.exe
