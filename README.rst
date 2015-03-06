==============
counterpart(s)
==============
-------------------------------------------------------------
Configuration file-driven values for shell and Python scripts
-------------------------------------------------------------

The ``counterparts`` module takes mappings, specified via files in the
``ConfigParser[1]`` format (default file name: ``.counterc``), and
uses them to look up a string value corresponding to each string that
it is given.  For example, given a file with a different path in your
present tree than in another tree, when generating a list of files,
you might wish to automatically substitute that other tree's path (the
counterpart of the present path).  First you would keep a list of
those special cases in a human-readable config file, and second,
arrange to let your shell or Python script use whatever
``counterparts`` finds.

The ``counterpart`` command provides shell access to the string
mapping abilities of the ``counterparts`` module.  Help for that
command is available[2] by running ``counterpart --help``.

Notice the slightly different names of ``counterpart`` (the shell
command) and ``counterparts`` (the Python module).  Besides giving a
clue as to which is being referred to, the choice of names reflects
that the command *is for looking up a counterpart* whereas the module
*is a more general treatment of counterparts*.  Except where noted,
the ``counterpart`` command and the ``counterparts`` module behave the
same: The command is essentially a front-end to the module's
``get_counterpart_mapping`` function; it runs the input string(s)
through the returned mapping, echoing the results as specified.

.. [1] https://docs.python.org/2/library/configparser.html
.. [2] ``counterpart`` is available after installing ``counterparts``
   and updating your ``PATH`` environment variable if necessary.


Requirements
============

Python 2.6+ and Python 3 are supported.

Tests have been run (and passed) on:

  * Mac OS X 10.5 and 10.8, using Python 2.7 and 3.4.


Installation
============

``pip`` is the recommended way to obtain and install ``counterparts``::

  pip install counterparts

Written in Python, this package's source code is on GitHub::

  git clone https://github.com/lionel/counterparts

From the top-level source directory, the usual ``setuptools`` operations
are available, i.e.::

  python setup.py install


Usage Summary
=============

By default, ``counterparts`` tries to read both ``~/.counterc`` and
``./.counterc``.  Their existence is optional.  Any additional config
files specified by the caller are mandatory.  In general,
``ConfigParser`` overrides earlier values with ones from files read
later, so values in a user-supplied config file take precedence over
the default files when they exist.

Given a ``.counterc`` file in the PWD containing::

  [COUNTERPART_MAP]
  foo = bar

Using the ``counterpart`` command::

  $ counterpart foo
  bar
  $

  $ diff foo `counterpart foo`
  # output diff between foo and bar

  $ counterpart baz
  Traceback (most recent call last):
  ... 
  KeyError: 'Mapping not found in COUNTERPART_MAP: baz'
  $

Because ``counterparts`` expects ``ConfigParser``-format files, the
sections in ``[SQUARE BRACES]`` are case sensitive, but the *option*
lines (left-hand side) ignore case.  Therefore, in the above config
example: ``foo``, ``Foo``, and ``FOO`` would all map to ``bar``, even
though ``[COUNTERPART_map]`` will **not** work correctly in place of
``[COUNTERPART_MAP]``.
  
Next, using the ``counterparts`` module::

  import counterparts
  before = "foo"
  after = counterparts.map_counterpart(before)

  # or, to avoid need for repeated map_counterpart calls to re-read config file(s):
  mapping = counterparts.get_counterpart_mapping()
  after = mapping[before]
  # the variable 'after' is assigned the value '"bar"'

You can specify, via a ``COUNTERPART_DIR`` section, a default mapping
for strings ("paths" in this case) that are not listed in the
``COUNTERPART_MAP``.  The ``prepend_path`` option in the
``COUNTERPART_DIR`` section tells ``counterparts`` to prepend its value
to any input that doesn't hit in the ``COUNTERPART_MAP``.

So, for example, given the ``.counterc``::

  [DEFAULT]
  up = ..
  [COUNTERPART_MAP]
  foo = %(home)s/bar
  [COUNTERPART_DIR]
  prepend_path = %(up)s/quux

  $ counterpart baz
  ../quux/baz
  $

The previous ``.counterc`` example also shows another feature:
``home`` is pre-populated in the ``DEFAULT`` section.  Hence, you can
manually provide a path relative to ``$HOME`` to use in the other
sections' right-hand-side values::

  $ [ `counterpart foo` == "$HOME/bar" ] && echo '%(home)s equals $HOME'
  %(home)s equals $HOME
  $

Finally, ``counterparts`` also supports an ``INCLUDE`` directive.  It
is specified as a section by that same name, and it accepts a
``paths`` option, which is a newline-separated list of one or more
other config files.  Some files that demonstrate valid uses of the
``INCLUDE`` section are:

* ``tests/counterparts_data/conf-include-logging``
* ``tests/counterparts_data/conf-include-more``
* ``tests/counterparts_data/conf-2-with-include``
* ``tests/counterparts_data/conf-include-still-more``

The ``INCLUDE`` section has proven useful for things like controlling
logging, setting site-specific options, and picking up global
defaults.


Configuration File
==================

The configuration file is in the format used by the ``ConfigParser``
module.  See Documentation_, below, for more about the format.

The special sections and options used by ``counterparts`` are
described above in the `Usage Summary`_.

The *sections* and *options* can be read from the config files of
other applications, as long as those applications ignore unknown
sections and ``counterparts`` is told to look in those files.

If no configuration file is provided to ``counterparts``, it looks
first in ``./.counterc`` and second in ``~/.counterc``.


Documentation
=============

For the most part, you're looking at it.

For some useful information on ``ConfigParser``-format files, see::

  https://docs.python.org/2/library/configparser.html


License
=======

``counterparts`` is released under the GPLv2, contained in the ``LICENSE.txt`` file.


Authors
=======

Copyright (c) 2015 by Lionel D. Hummel.


Roadmap
=======

I put ``counterparts`` up on GitHub to give me a bite-sized (but
meaningful) sample with which to explore the site's features such as
continuous integration and documentation.  So this is what I've got
for its roadmap so far:

* More tests and documentation are needed.

I'm glad to discuss an expanded roadmap if ``counterparts`` proves
useful to any contributors besides myself.



Contributing
============

``counterparts`` is meant to be a solid, idiomatic, and readable
example of Python code.  I can think of several ways it is not quite
there yet in this release.  If you've got one in mind, please use the
GitHub page to contact the author, ask questions, report bugs, suggest
patches, receive updates, etc.::

    https://github.com/lionel/counterparts
