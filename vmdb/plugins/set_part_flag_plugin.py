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


class SetPartFlagPlugin(vmdb.Plugin):
    def enable(self):
        self.app.step_runners.add(SetPartFlagStepRunner())


class SetPartFlagStepRunner(vmdb.StepRunnerInterface):
    def get_key_spec(self):
        return {
            "set_part_flag": str,
            "tag": str,
            "flag": str,
            "state": "enabled"
        }

    def run(self, values, settings, state):
        device = values["set_part_flag"]
        tag = values["tag"]
        flag = values["flag"]
        flag_state = values["state"]

        if flag_state == "enabled":
            flag_state = "on"
        elif flag_state == "disabled":
            flag_state = "off"
        else:
            raise SetPartFlagError('state must be "enabled" or "disabled"')

        tags_list = state.tags.get_tags()
        try:
            partition_number = tags_list.index(tag) + 1
        except IndexError:
            raise SetPartFlagError(f"Didn't find tag {tag} in {tags_list}")

        device = os.path.realpath(device)
        vmdb.runcmd([
            "parted", "-s", device, "--", "set",
            str(partition_number), flag, flag_state
        ])


class SetPartFlagError(Exception):
    pass
