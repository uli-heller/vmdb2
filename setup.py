#!/usr/bin/env python3
# Copyright (C) 2017  Lars Wirzenius <liw@liw.fi>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from distutils.core import setup
import glob


import vmdb


setup(
    name="vmdb2",
    version=vmdb.__version__,
    description="create disk image with Debian installed",
    author="Lars Wirzenius",
    author_email="liw@liw.fi",
    url="http://liw.fi/vmdebootstrap/",
    scripts=["vmdb2"],
    packages=["vmdb", "vmdb.plugins"],
    data_files=[("share/man/man1", glob.glob("*.1"))],
)
