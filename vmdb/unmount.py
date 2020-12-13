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


# Unmount a directory, including any mount points under that
# directory. If /mnt/foo is given, and /mnt/foo/bar is also mounted,
# unmount /mnt/foo/bar first, and /mnt/foo then. Look for sub-mounts
# in /proc/mounts.


import logging
import subprocess


def unmount(what, mounts=None, real_unmount=None):
    logging.debug("Unmounting {} and everything on top of it".format(what))
    if mounts is None:  # pragma: no cover
        mounts = _read_proc_mounts()
    if real_unmount is None:  # pragma: no cover
        real_unmount = _real_unmount

    mounts = _parse_proc_mounts(mounts)
    dirnames = _find_what_to_unmount(mounts, what)
    for dirname in dirnames:
        real_unmount(dirname)
    logging.debug("Finished unmounting {}".format(what))


def _read_proc_mounts():  # pragma: no cover
    with open("/proc/mounts") as f:
        return f.read()


def _real_unmount(what):  # pragma: no cover
    try:
        subprocess.check_call(["umount", what])
    except subprocess.CalledProcessError as e:
        logging.info("unmount failed, but ignoring that: %s", e)


def _parse_proc_mounts(text):
    return [line.split()[:2] for line in text.splitlines()]


def _find_what_to_unmount(mounts, what):
    dirname = _find_mount_point(mounts, what)
    dirnameslash = dirname + "/"
    to_unmount = [
        point
        for dev, point in mounts
        if point == dirname or point.startswith(dirnameslash)
    ]
    return list(reversed(sorted(to_unmount)))


def _find_mount_point(mounts, what):
    for dev, point in mounts:
        if what in (dev, point):
            return point
    raise NotMounted(what)


class NotMounted(Exception):
    def __init__(self, what):
        super().__init__("Not mounted: {}".format(what))
