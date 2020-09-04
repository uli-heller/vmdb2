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


import importlib.util
import os


class Plugin:
    def __init__(self, app):
        self.app = app


def find_plugins(dirname, namesuffix):
    suffix = "_plugin.py"
    filenames = _find_suffixed_files(dirname, suffix)
    plugins = []
    for filename in filenames:
        for c in _classes_in_file(filename, namesuffix):
            plugins.append(c)

    return plugins


def _find_suffixed_files(dirname, suffix):
    return [
        os.path.join(dirname, basename)
        for basename in os.listdir(dirname)
        if basename.endswith(suffix)
    ]


def _classes_in_file(filename, namesuffix):
    module_name = os.path.basename(filename)[: -len(".py")]
    spec = importlib.util.spec_from_file_location(module_name, filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    classes = []
    for name in dir(module):
        if name.endswith(namesuffix):
            classes.append(module.__getattribute__(name))
    return classes
