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


class ErrorPlugin(cliapp.Plugin):

    def enable(self):
        self.app.step_runners.add(ErrorStepRunner())


class ErrorStepRunner(vmdb.StepRunnerInterface):

    def get_key_spec(self):
        return {
            'error': str,
            'teardown': str,
        }

    def get_required_keys(self):
        return ['error', 'teardown']

    def run(self, values, settings, state):
        # We use vmdb.progress here to get output to go to stdout,
        # instead of stderr. We want that for tests.
        vmdb.progress('{}'.format(values['error']))
        raise vmdb.StepError('an error occurred')

    def teardown(self, values, settings, state):
        # We use vmdb.progress here to get output to go to stdout,
        # instead of stderr. We want that for tests.
        vmdb.progress('{}'.format(values['teardown']))
