# Copyright 2021  Andy Piper
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

import vmdb


class ZerofreePlugin(vmdb.Plugin):
    def enable(self):
        self.app.step_runners.add(ZerofreeStepRunner())


class ZerofreeStepRunner(vmdb.StepRunnerInterface):
    def get_key_spec(self):
        return {"zerofree": str}

    def run(self, values, settings, state):
        tag = values["zerofree"]
        dev = state.tags.get_dev(tag)
        mount_point = state.tags.get_builder_mount_point(tag)
        try:
            vmdb.runcmd(["mount", "-o", "remount,ro", mount_point])
            vmdb.runcmd(["zerofree", "-v", dev])
        finally:
            vmdb.runcmd(["mount", "-o", "remount,rw", mount_point])
