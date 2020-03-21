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


class LvcreatePlugin(cliapp.Plugin):

    def enable(self):
        self.app.step_runners.add(LvcreateStepRunner())


class LvcreateStepRunner(vmdb.StepRunnerInterface):

    def get_key_spec(self):
        return {
            'lvcreate': str,
            'name': str,
            'size': str,
        }

    def run(self, values, settings, state):
        vgname = values['lvcreate']
        lvname = values['name']
        size = values['size']

        vmdb.runcmd(['lvcreate', '--name', lvname, '--size', size, vgname])

        lvdev = '/dev/{}/{}'.format(vgname, lvname)
        assert os.path.exists(lvdev)
        state.tags.append(lvname)
        state.tags.set_dev(lvname, lvdev)
