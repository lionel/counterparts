#!/usr/bin/env python
# -*- mode: python -*-
"""
    counterparts
    ____________

    Lookup a counterpart string/file based on some name/path mapping.

    :copyright: (c) 2015 by Lionel D. Hummel
    :license: GPLv2; see LICENSE.txt for more details.

    For more info:  http://github.com/lionel/counterparts
"""

import sys
import os
import argparse
import logging
import logging.config

import platform
py_major_str, __, __ = platform.python_version_tuple()
if int(py_major_str) >= 3:
    import configparser as config_parser
    ConfigParser = config_parser.ConfigParser
else:
    import ConfigParser as config_parser
    ConfigParser = config_parser.SafeConfigParser

__version__ = "0.1"

config_file_basename = ".counterc"

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class RecursionInConfigFile(ValueError):
    pass


class FileNotFound(IOError):
    pass


class CounterpartMapping:
    """This class carries the pieces needed to perform mappings.

    Sections represent groups that enable this mapping to apply
    different rules depending on attributes of the input.  The two
    sections here are COUNTERPART_MAP and COUNTERPART_DIR.

    CounterpartMapping is much like a collections.Mapping, but it does
    not support the __iter__ and __len__ methods specified for that
    class.  Unlike mapping functions with a fixed set of keys, the
    domain may be unknown when the COUNTERPART_DIR section is present
    in the config.

    """
    def __init__(self, map_config):

        logger.debug("NEW: CounterpartMapping w/%s", map_config)
        self._map_config = map_config

    def __getitem__(self, known):
        """If the counterpart is named explicitly in COUNTERPART_MAP, return
        it.  When `prepend_path` is given in the COUNTERPART_DIR
        section, it is prepended to all input that lacks an explicitly
        named counterpart in COUNTERPART_MAP.

        """

        try:
            counterpart = self._map_config.get("COUNTERPART_MAP", known)
            logger.debug("Result for %s: %s", known, counterpart)
        except (config_parser.NoSectionError, config_parser.NoOptionError):
            try:
                msg = "Nothing for '%s';" % (known)
                prepend = self._map_config.get("COUNTERPART_DIR",
                                               "prepend_path")
                counterpart = os.path.join(prepend, os.path.relpath(known))
                logger.debug("%s result with prepend (%s): %s",
                             msg, prepend, counterpart)
            except config_parser.NoSectionError:
                logger.debug("%s (and no prepend_path)", msg)
                raise KeyError("Mapping not found in COUNTERPART_MAP: " +
                               "%s" % (known))

        return counterpart


class ConfigFromFile:

    rc_file_basename = config_file_basename
    shared_environ = {'home': os.environ["HOME"]}

    def __init__(self, config_file=None,
                 add_rc_files=[], skip_file_read=[]):
        """Only the "implicit" paths are optional; if they or any other files
        are passed as config_file or in add_rc_files (and not supposed
        to be skipped), they are required.

        """
        logger.debug("config_file = %s, " % (config_file) +
                     "add_rc_files = %s, " % (add_rc_files) +
                     "skip_file_read = %s " % (skip_file_read))
        self._local_rc_file = config_file or self.rc_file_basename
        self._parsed_files = []
        parser = ConfigParser(defaults=self.shared_environ,
                              allow_no_value=True)
        self._parser = parser
        files_to_parse = [f for f in ([self.home_rc_file_path,
                                       self._local_rc_file] +
                                      add_rc_files)
                          if f not in skip_file_read]
        for f in files_to_parse:
            optional_flag = (f is not config_file and
                             f not in add_rc_files)
            self._handle_rc_file(f, optional_flag)

    @property
    def home_rc_file_path(self):

        return os.path.join(os.getenv('HOME'), self.rc_file_basename)

    @classmethod
    def register_options(this_class, argparser):
        """This class method is called so that ConfigFromFile can tell the
        command-line parser to register the options specific to the class.

        :param this_class: Not used (required by @classmethod interface)
        :param argparser: The argparser instance being prepared for use.

        """
        default_path = this_class.rc_file_basename
        default_basename = os.path.basename(default_path)
        argparser.add_argument('-c', "--config-file",
                               default=default_path,
                               help=("Configuration file to use for lookups " +
                                     "(replaces DEFAULT=%s " % (default_path) +
                                     "but not ~/%s)" % (default_basename)))

    def _check_and_handle_includes(self, from_file):
        """Look for an optional INCLUDE section in the given file path.  If
        the parser set `paths`, it is cleared so that they do not keep
        showing up when additional files are parsed.

        """
        logger.debug("Check/handle includes from %s", from_file)
        try:
            paths = self._parser.get("INCLUDE", "paths")
        except (config_parser.NoSectionError,
                config_parser.NoOptionError) as exc:
            logger.debug("_check_and_handle_includes: EXCEPTION: %s", exc)
            return
        paths_lines = [p.strip() for p in paths.split("\n")]
        logger.debug("paths = %s (wanted just once; CLEARING)", paths_lines)
        self._parser.remove_option("INCLUDE", "paths")
        for f in paths_lines:
            abspath = (f if os.path.isabs(f) else
                       os.path.abspath(
                           os.path.join(os.path.dirname(from_file), f)))
            use_path = os.path.normpath(abspath)
            if use_path in self._parsed_files:
                raise RecursionInConfigFile("In %s: %s already read",
                                            from_file, use_path)
            self._parsed_files.append(use_path)
            self._handle_rc_file(use_path)

    def _handle_rc_file(self, from_file, optional_flag=True):

        logger.debug("path=%s, optional=%s", from_file, optional_flag)
        self._parsed_files.append(from_file)
        success = self._parser.read(from_file)
        if not success and not optional_flag:
            logger.debug("unsuccessful read of %s from %s",
                         from_file, os.getcwd())
            if not os.path.exists(from_file):
                raise FileNotFound(from_file)
            else:
                raise IOError("ConfigParser for %s", from_file)
        logger.debug("successful read of %s = %s", from_file, success)
        self._check_and_handle_includes(from_file)


def counterpart_found(string, counterpart, options, rc_so_far):
    """The sunny-day action is to echo the counterpart to stdout.

    :param string: The lookup string  (UNUSED)
    :param counterpart: The counterpart that the string mapped to
    :param options: ArgumentParser or equivalent to provide options.no_newline
    :param rc_so_far: Stays whatever value it was.
    """
    format = "%s" if options.no_newline else "%s\n"
    sys.stdout.write(format % (counterpart))
    return rc_so_far or 0


def no_counterpart_found(string, options, rc_so_far):
    """Takes action determined by options.else_action.  Unless told to
    raise an exception, this function returns the errno that is supposed
    to be returned in this case.

    :param string: The lookup string.
    :param options: ArgumentParser or equivalent to provide
        options.else_action, options.else_errno, options.no_newline
    :param rc_so_far: Becomes set to the value set in options.

    """
    logger.debug("options.else_action: %s", options.else_action)
    if options.else_action == "passthrough":
        format_list = [string]
        output_fd = sys.stdout
    elif options.else_action == "exception":
        raise KeyError("No counterpart found for: %s" % (string))
    elif options.else_action == "error":
        format_list = ["# No counterpart found for: %s" % (string)]
        output_fd = sys.stderr
    if not options.no_newline:
        format_list.append("\n")
    output_fd.write("".join(format_list))
    return options.else_errno


def get_counterpart_mapping(config_file=None, skip_home=False):
    """Initial part of a two-step lookup: First load the mapping
    (CounterpartMapping) with this function.  The mapping can then be
    subscripted to look up specific counterparts' mappings.  This way
    is more efficient than calling map_counterpart several times,
    because it reads the config file(s) only once.

    :param config_file: Path to a config file to guide the mapping.
           Default is to use ./counterc and/or ~/.countrc.
    :param skip_home: If True, only the config_file is read.
    :return: CounterpartMapping loaded from config_file et al.

    """
    file_skip_list = ([ConfigFromFile.home_rc_file_path]
                      if skip_home else [])
    config = ConfigFromFile(config_file, [], skip_file_read=file_skip_list)
    return CounterpartMapping(map_config=config._parser)


def map_counterpart(string, config_file=None):
    """One-step look-up; returns a counterpart for the given string, as
    determined from the config file(s) via ConfigFromFile.
    config_file is read after ~/.counterc, if present, making its
    values take precedence over those in ~/.counterc.

    :param string: The string to find the counterpart of.
    :param config_file: Path to a config file to guide the mapping.
           Default is to use ./counterc and/or ~/.countrc.
    :return: String value, the counterpart of the input string.

    """
    skip_home_flag = config_file is not None
    mapping = get_counterpart_mapping(config_file, skip_home_flag)
    return mapping[string]


def _generate_input(options):
    """First send strings from any given file, one string per line, sends
    any strings provided on the command line.

    :param options: ArgumentParser or equivalent to provide
        options.input and options.strings.
    :return: string

    """
    if options.input:
        fp = open(options.input) if options.input != "-" else sys.stdin
        for string in fp.readlines():
            yield string
    if options.strings:
        for string in options.strings:
            yield string


def main(argv=sys.argv):

    logger.debug("Invoked as %s from %s", argv[0], os.getcwd())
    parser = argparse.ArgumentParser(prog="counterpart")
    parser.add_argument("-a", "--else-action", type=str, default="exception",
                        choices=["passthrough", "silent",
                                 "error", "exception"],
                        help=("Action if missing: " +
                              "\"passthrough\" outputs the original input.  " +
                              "\"silent\" echoes nothing.  " +
                              "\"error\" prints a message to stderr.  " +
                              "\"exception\" raises a KeyError.  " +
                              "The default is \"%(default)s\"."))
    parser.add_argument("-e", "--else-errno", type=int, default=1,
                        help=("Return code when no mapping is found " +
                              "(default is 1; 0 == no error)"))
    parser.add_argument("-i", "--input", default=None,
                        metavar="INPUT_FILE",
                        help=("Take input strings from the given file " +
                              "or '-' for STDIN."))
    parser.add_argument("-n", "--no-newline", action="store_true",
                        help="Print output without a trailing newline.")
    parser.add_argument("-V", "--version", action="version",
                        version="counterpart: Version %s" % (__version__),
                        help="Report version info and exit.")
    parser.add_argument("strings", nargs="*")
    ConfigFromFile.register_options(parser)
    options = parser.parse_args()
    mapping = get_counterpart_mapping(options.config_file)
    rc_so_far = 0
    for p in _generate_input(options):
        try:
            counterpart_string = mapping[p]
            rc_so_far = counterpart_found(p, counterpart_string,
                                          options, rc_so_far)
        except KeyError:
            rc_so_far = (1 if options.else_action == "silent" else
                         no_counterpart_found(p, options,
                                              rc_so_far))
    return rc_so_far


if __name__ == "__main__":
    try:
        logging.config.fileConfig(os.path.join(os.getenv('HOME'),
                                               config_file_basename))
        logger = logging.getLogger()
    except config_parser.NoSectionError:
        pass
    rc = main()
    sys.exit(rc)
