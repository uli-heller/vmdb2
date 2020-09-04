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


import vmdb


class VgcreatePlugin(vmdb.Plugin):
    def enable(self):
        self.app.step_runners.add(VgcreateStepRunner())


class VgcreateStepRunner(vmdb.StepRunnerInterface):
    def get_key_spec(self):
        return {"vgcreate": str, "physical": []}

    def run(self, values, settings, state):
        vgname = self.get_vg(values)
        physical = self.get_pv(values, state)

        for phys in physical:
            vmdb.runcmd(["pvcreate", "-ff", "--yes", phys])
        vmdb.runcmd(["vgcreate", vgname] + physical)

    def teardown(self, values, settings, state):
        vgname = self.get_vg(values)
        vmdb.runcmd(["vgchange", "-an", vgname])

    def get_vg(self, values):
        return values["vgcreate"]

    def get_pv(self, values, state):
        return [state.tags.get_dev(tag) for tag in values["physical"]]
