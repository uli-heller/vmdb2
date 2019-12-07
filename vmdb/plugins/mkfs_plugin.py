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
import logging

import vmdb


class NotString(vmdb.StepError):

    def __init__(self, name, actual):
        msg = '%s: value must be string, got %r' % (name, actual)
        super().__init__(msg)


class MkfsPlugin(cliapp.Plugin):

    def enable(self):
        self.app.step_runners.add(MkfsStepRunner())


class MkfsStepRunner(vmdb.StepRunnerInterface):

    def get_required_keys(self):
        return ['mkfs', 'partition']

    def run(self, step, settings, state):
        fstype = step['mkfs']
        tag = step['partition']
        device = state.tags.get_dev(tag)

        logging.debug('state: %r', state.as_dict())
        if not isinstance(fstype, str):
            raise NotString('mkfs', fstype)
        if not isinstance(tag, str):
            raise NotString('mkfs: tag', tag)
        if not isinstance(device, str):
            raise NotString('mkfs: device (for tag)', device)

        cmd = ['/sbin/mkfs', '-t', fstype]
        if 'label' in step:
            if fstype == 'vfat':
                cmd.append('-n')
            elif fstype == 'f2fs':
                cmd.append('-l')
            else:
                cmd.append('-L')
            cmd.append(step['label'])
        cmd.append(device)
        vmdb.runcmd(cmd)
