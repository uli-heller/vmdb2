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
import stat

import cliapp

import vmdb


class MklabelPlugin(cliapp.Plugin):
    def enable(self):
        self.app.step_runners.add(MklabelStepRunner())


class MklabelStepRunner(vmdb.StepRunnerInterface):
    def get_key_spec(self):
        return {"mklabel": str, "device": str}

    def run(self, values, settings, state):
        label_type = values["mklabel"]
        device = values["device"]
        vmdb.runcmd(["parted", "-s", device, "mklabel", label_type])
