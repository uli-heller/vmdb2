# Copyright 2020  Lars Wirzenius
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# =*= License: GPL-3+ =*=


import os
import shutil
import tempfile
import unittest


import vmdb


class PluginTests(unittest.TestCase):
    def test_sets_app(self):
        plugin = vmdb.Plugin("foo")
        self.assertEqual(plugin.app, "foo")


class FindPluginsTests(unittest.TestCase):
    def setUp(self):
        self.dirname = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.dirname)

    def tests_finds_no_plugins_in_empty_directory(self):
        self.assertEqual(vmdb.find_plugins(self.dirname, ""), [])

    def tests_finds_no_plugins_when_there_are_other_files(self):
        open(os.path.join(self.dirname, "file.py"), "w").close()
        self.assertEqual(vmdb.find_plugins(self.dirname, ""), [])

    def tests_finds_no_plugin_when_file_has_none(self):
        open(os.path.join(self.dirname, "foo_plugin.py"), "w").close()
        self.assertEqual(vmdb.find_plugins(self.dirname, "Plugin"), [])

    def tests_finds_plugin_when_there_is_one(self):
        with open(os.path.join(self.dirname, "foo_plugin.py"), "w") as f:
            f.write(
                """
class FooPlugin:
   pass
"""
            )

        plugins = vmdb.find_plugins(self.dirname, "Plugin")
        self.assertEqual(len(plugins), 1)
