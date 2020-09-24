# Copyright 2017  Lars Wirzenius
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


import logging
import os

import vmdb


class UnpackRootFSPlugin(vmdb.Plugin):
    def enable(self):
        self.app.step_runners.add(UnpackCacheStepRunner())


class UnpackCacheStepRunner(vmdb.StepRunnerInterface):
    def get_key_spec(self):
        return {"unpack-rootfs": str}

    def run(self, values, settings, state):
        fs_tag = values["unpack-rootfs"]
        rootdir = state.tags.get_builder_mount_point(fs_tag)
        logging.debug(f"settings: {settings}")
        tar_path = settings["rootfs-tarball"]
        logging.debug(f"tar_path: {tar_path!r}")
        if not tar_path:
            raise Exception("--rootfs-tarball MUST be set")
        if os.path.exists(tar_path):
            vmdb.runcmd(["tar", "-C", rootdir, "-xf", tar_path, "--numeric-owner"])
            self.copy_resolv_conf(rootdir)
            state.rootfs_unpacked = True

    def copy_resolv_conf(self, rootdir):
        filename = os.path.join(rootdir, "etc", "resolv.conf")
        vmdb.runcmd(["cp", "/etc/resolv.conf", filename])
