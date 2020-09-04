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
import tempfile

import vmdb


class MountPlugin(vmdb.Plugin):
    def enable(self):
        self.app.step_runners.add(MountStepRunner())


class MountStepRunner(vmdb.StepRunnerInterface):
    def get_key_spec(self):
        return {"mount": str, "dirname": "", "mount-on": ""}

    def run(self, values, settings, state):
        self.mount_rootfs(values, settings, state)

    def teardown(self, values, settings, state):
        self.unmount_rootfs(values, settings, state)

    def mount_rootfs(self, values, settings, state):
        tag = values["mount"]
        dirname = values["dirname"] or None
        mount_on = values["mount-on"] or None

        device = state.tags.get_dev(tag)

        if dirname:
            if not mount_on:
                raise Exception("no mount-on tag given")

            if not state.tags.has_tag(mount_on):
                raise Exception("cannot find tag {}".format(mount_on))

            mount_point = os.path.join(
                state.tags.get_builder_mount_point(mount_on), "./" + dirname
            )

            if not os.path.exists(mount_point):
                os.makedirs(mount_point)
        else:
            dirname = "/"
            mount_point = tempfile.mkdtemp()

        vmdb.runcmd(["mount", device, mount_point])
        state.tags.set_builder_mount_point(tag, mount_point, cached=True)
        state.tags.set_target_mount_point(tag, dirname)

        return mount_point

    def unmount_rootfs(self, values, settings, state):
        tag = values["mount"]
        mount_point = state.tags.get_builder_mount_point(tag)
        if mount_point is None:
            return

        try:
            vmdb.unmount(mount_point)
        except vmdb.NotMounted as e:
            logging.warning(str(e))

        if not values["mount-on"]:
            os.rmdir(mount_point)
