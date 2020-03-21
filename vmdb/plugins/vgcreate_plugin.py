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



import os

import cliapp

import vmdb


class VgcreatePlugin(cliapp.Plugin):

    def enable(self):
        self.app.step_runners.add(VgcreateStepRunner())


class VgcreateStepRunner(vmdb.StepRunnerInterface):

    def get_required_keys(self):
        return ['vgcreate', 'physical']

    def run(self, step, settings, state):
        vgname = self.get_vg(step)
        physical = self.get_pv(step, state)

        for phys in physical:
            vmdb.runcmd(['pvcreate', '-ff', '--yes', phys])
        vmdb.runcmd(['vgcreate', vgname] + physical)

    def teardown(self, step, settings, state):
        vgname = self.get_vg(step)
        vmdb.runcmd(['vgchange', '-an', vgname])

    def get_vg(self, step):
        return step['vgcreate']

    def get_pv(self, step, state):
        return [
            state.tags.get_dev(tag)
            for tag in step['physical']
        ]
