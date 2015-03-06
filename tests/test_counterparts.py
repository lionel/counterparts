
import unittest
import os

import counterparts


class MockOpts:

    def __init__(self, config_file=None):

        self.config_file = config_file
        self.no_newline = False
        self.version = False


def under_home(p):

    return os.path.join(os.getenv("HOME"), p)


def under_src(p):

    return os.path.join(os.getenv("HOME"), "src/HummelAbode/src", p)


class TestCounterparts(unittest.TestCase):

    def setUp(self):

        # goes here
        pass

    def _conf_path(self, name):

        config_dir = os.path.join(os.path.dirname(__file__),
                                  "counterparts_data")
        config_file = os.path.join(config_dir, name)
        return config_file

    def _conf_accessible(self, name):

        return os.path.exists(self._conf_path(name))

    def _read_mapping(self, name):

        mapping = counterparts.get_counterpart_mapping(self._conf_path(name),
                                                       skip_home=True)
        return mapping

    def test_conf_0_accessible(self):

        self.assertTrue(self._conf_accessible("conf-0"))

    def test_conf_0_missing(self):

        self.assertFalse(self._conf_accessible("missing"))
        options = MockOpts(self._conf_path("missing"))
        skip_files = [counterparts.ConfigFromFile.home_rc_file_path]
        self.assertRaises(counterparts.FileNotFound,
                          counterparts.ConfigFromFile,
                          options.config_file,
                          skip_file_read=skip_files)

    def test_conf_recursion(self):

        options = MockOpts(self._conf_path("conf-recursive"))
        skip_files = [counterparts.ConfigFromFile.home_rc_file_path]
        self.assertRaises(counterparts.RecursionInConfigFile,
                          counterparts.ConfigFromFile,
                          options.config_file,
                          skip_file_read=skip_files)

    def test_conf_1_in_default(self):
        """Mappings come from COUNTERPART_MAP sections, not DEFAULT sections.

        """
        mapping = self._read_mapping("conf-1-in-default")
        self.assertRaises(KeyError,
                          mapping.__getitem__,
                          "counterpart")

    def test_conf_1_overrides_default(self):
        """The same option in both sections will return the value in the
        COUNTERPART_MAP section (counterparts.py, not counterpart.py).

        """
        mapping = self._read_mapping("conf-1-overrides-default")
        self.assertEqual(mapping["counterpart"], "counterparts.py")
        self.assertEqual(mapping["from_default"], "counterparts.py")
        self.assertEqual(mapping["from_counterparts"], "counterparts.py")

    def test_conf_2(self):

        mapping = self._read_mapping("conf-2")
        self.assertRaises(KeyError,
                          mapping.__getitem__,
                          "bashlib")
        self.assertEqual(mapping["bashlib/bashlib"],
                         under_home("lib/bashlib"))
        self.assertEqual(mapping["bashlib/lib"],
                         under_home("lib/bash"))
        self.assertEqual(mapping["bashlib/lib_local"],
                         under_home("lib/bash_local"))

    def test_conf_2_via_map_counterpart(self):

        conf_2_path = self._conf_path("conf-2")
        self.assertRaises(KeyError,
                          counterparts.map_counterpart,
                          "bashlib",
                          config_file=conf_2_path)
        self.assertEqual(counterparts.map_counterpart("bashlib/bashlib",
                                                      config_file=conf_2_path),
                         under_home("lib/bashlib"))

    def test_conf_2_with_include(self):

        mapping = self._read_mapping("conf-2-with-include")
        hostname = "test-host.local"
        self.assertEqual(mapping["lib/bash_local"],
                         under_src("bashlib/lib_local/%s" % (hostname)))

    def test_conf_2_without_include(self):

        mapping = self._read_mapping("conf-2-without-include")
        hostname = "test-host.local"
        self.assertEqual(mapping["lib/bash_local"],
                         under_src("bashlib/lib_local/%s" % (hostname)))

    def test_include_logging(self):

        mapping = self._read_mapping("conf-include-logging")
        self.assertEqual(mapping["conf-logging"], ".counterc")

    def test_include_more(self):

        mapping = self._read_mapping("conf-include-still-more")
        self.assertEqual(mapping["paths"],
                         "source/bash/00_std_paths")
        self.assertEqual(mapping["lib/bashpaths"],
                         "source/bashpaths")
        self.assertEqual(mapping["paths_ref"],
                         "source/bash/00_std_paths")
        self.assertEqual(mapping["src"],
                         "source")

    def test_vars_ne_mappings(self):

        mapping = self._read_mapping("conf-map-home")
        self.assertEqual(mapping["home"], "playground")

    def test_conf_peer_dir(self):

        if int(counterparts.py_major_str) >= 3:
            self.assertRaises(counterparts.config_parser.DuplicateOptionError,
                              self._read_mapping,
                              "conf-peer-0")
            return

        mapping = self._read_mapping("conf-peer-0")
        self.assertEqual(mapping[".emacs"],
                         under_home(".emacs"))
        self.assertEqual(mapping["lion-emacs-init.el"],
                         under_home(".emacs"))
        self.assertEqual(mapping["lion-unison.el"],
                         under_home("emacs/lisp/other/lion-unison.el"))
        self.assertEqual(mapping["lion-whence.el"],
                         under_home("emacs/lisp/whence.el"))
        self.assertEqual(mapping["splay.el"],
                         under_home("other/splay.el"))
        self.assertEqual(mapping["ldh-org.el"],
                         under_home("other/ldh-org.el"))
        self.assertEqual(mapping[".counterc"],
                         under_home("src/counterparts/.counterc"))

    def test_default_conf_ordering(self):
        """~/.counterc and ./.counterc are read first, if they exist.  Because
        they are obtained more recently, values in the PWD shadow
        those in HOME.

        """

        current_dir = os.getcwd()
        home_dir = os.environ["HOME"]
        uniq = ".counterc_unittest"
        uniq_in_current = os.path.join(current_dir, uniq)
        uniq_in_home = os.path.join(home_dir, uniq)

        counterparts.ConfigFromFile.rc_file_basename = uniq

        for f in [uniq_in_current, uniq_in_home]:
            with open(f, 'w') as fp:
                fp.write("[COUNTERPART_MAP]\noption_source = %s" % f)

        self.assertEqual(counterparts.map_counterpart("option_source"),
                         uniq_in_current)
        os.remove(uniq_in_current)
        self.assertEqual(counterparts.map_counterpart("option_source"),
                         uniq_in_home)
        os.remove(uniq_in_home)


if __name__ == "__main__":

    unittest.main()
