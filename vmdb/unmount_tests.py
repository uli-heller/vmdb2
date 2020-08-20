# Copyright 2018  Lars Wirzenius
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


import unittest


import vmdb


class UnmountTests(unittest.TestCase):
    def setUp(self):
        self.mounts = ProcMounts()

    def unmount(self, what):
        vmdb.unmount(what, mounts=str(self.mounts), real_unmount=self.mounts.unmount)

    def test_raises_error_if_not_mounted(self):
        with self.assertRaises(vmdb.NotMounted):
            self.unmount("/foo")

    def test_unmounts_mounted_dir(self):
        self.mounts.mount("/dev/foo", "/foo")
        self.unmount("/foo")
        self.assertFalse(self.mounts.is_mounted("/foo"))

    def test_unmounts_mounted_dir_with_submounts(self):
        self.mounts.mount("/dev/foo", "/foo")
        self.mounts.mount("/dev/bar", "/foo/bar")
        self.unmount("/foo")
        self.assertFalse(self.mounts.is_mounted("/foo"))
        self.assertFalse(self.mounts.is_mounted("/foo/bar"))


class ProcMounts:
    def __init__(self):
        self.mounts = []

    def is_mounted(self, what):
        return any(what in mount for mount in self.mounts)

    def mount(self, device, point):
        self.mounts.append((device, point))

    def unmount(self, what):
        self.mounts = [mount for mount in self.mounts if what not in mount]

    def __str__(self):
        return "".join("{}\n".format(self.mount_line(mount)) for mount in self.mounts)

    def mount_line(self, mount):
        return "{} {} fstype options 0 0".format(mount[0], mount[1])
