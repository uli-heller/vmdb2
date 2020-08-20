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


import cliapp

import vmdb


class MkfsPlugin(cliapp.Plugin):
    def enable(self):
        self.app.step_runners.add(MkfsStepRunner())


class MkfsStepRunner(vmdb.StepRunnerInterface):
    def get_key_spec(self):
        return {"mkfs": str, "partition": str, "label": ""}

    def run(self, values, settings, state):
        fstype = values["mkfs"]
        tag = values["partition"]
        device = state.tags.get_dev(tag)

        if not isinstance(fstype, str):
            raise vmdb.NotString("mkfs", fstype)
        if not isinstance(tag, str):
            raise vmdb.NotString("mkfs: tag", tag)
        if not isinstance(device, str):
            raise vmdb.NotString("mkfs: device (for tag)", device)

        cmd = ["/sbin/mkfs", "-t", fstype]
        label = values["label"] or None
        if label:
            if fstype == "vfat":
                cmd.append("-n")
            elif fstype == "f2fs":
                cmd.append("-l")
            else:
                cmd.append("-L")
            cmd.append(label)
        cmd.append(device)
        vmdb.runcmd(cmd)

        state.tags.set_fstype(tag, fstype)
