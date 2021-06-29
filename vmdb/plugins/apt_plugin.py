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


import os

import vmdb


class AptPlugin(vmdb.Plugin):
    def enable(self):
        self.app.step_runners.add(AptStepRunner())


class AptStepRunner(vmdb.StepRunnerInterface):
    def get_key_spec(self):
        return {"apt": str, "packages": [], "tag": "", "fs-tag": "", "clean": True, "recommends": True}

    def run(self, values, settings, state):
        operation = values["apt"]
        if operation != "install":
            raise Exception('"apt" must always have value "install"')

        packages = values["packages"]
        recommends = values["recommends"]
        tag = values.get("tag") or None
        if tag is None:
            tag = values["fs-tag"]
        mount_point = state.tags.get_builder_mount_point(tag)

        if not self.got_eatmydata(state):
            self.install_packages(mount_point, [], recommends, ["eatmydata"])
            state.got_eatmydata = True
        self.install_packages(mount_point, ["eatmydata"], recommends, packages)

        if values["clean"]:
            self.clean_cache(mount_point)

    def got_eatmydata(self, state):
        return hasattr(state, "got_eatmydata") and getattr(state, "got_eatmydata")

    def install_packages(self, mount_point, argv_prefix, recommends, packages):
        env = os.environ.copy()
        env["DEBIAN_FRONTEND"] = "noninteractive"

        vmdb.runcmd_chroot(mount_point, argv_prefix + ["apt-get", "update"], env=env)

        rec = ''
        if not recommends:
            rec = '--no-install-recommends'

        vmdb.runcmd_chroot(
            mount_point,
            argv_prefix + ["apt-get", "-y", "--no-show-progress", rec, "install"] + packages,
            env=env,
        )

    def clean_cache(self, mount_point):
        env = os.environ.copy()
        env["DEBIAN_FRONTEND"] = "noninteractive"

        vmdb.runcmd_chroot(mount_point, ["apt-get", "clean"], env=env)
