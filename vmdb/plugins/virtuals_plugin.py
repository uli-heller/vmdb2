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



import logging
import os

import cliapp

import vmdb


class VirtualFilesystemMountPlugin(cliapp.Plugin):

    def enable(self):
        self.app.step_runners.add(VirtualFilesystemMountStepRunner())


class VirtualFilesystemMountStepRunner(vmdb.StepRunnerInterface):

    virtuals = [
        ['none', '/proc', 'proc'],
        ['none', '/dev', 'devtmpfs'],
        ['none', '/dev/pts', 'devpts'],
        ['none', '/dev/shm', 'tmpfs'],
        ['none', '/run', 'tmpfs'],
        ['none', '/run/lock', 'tmpfs'],
        ['none', '/sys', 'sysfs'],
    ]

    def get_required_keys(self):
        return ['mount-virtual-filesystems']

    def run(self, step, settings, state):
        fstag = step['mount-virtual-filesystems']
        mount_point = state.tags.get_mount_point(fstag)
        self.mount_virtuals(mount_point, state)

    def teardown(self, step, settings, state):
        self.unmount_virtuals(state)

    def mount_virtuals(self, rootfs, state):
        if not hasattr(state, 'virtuals'):
            state.virtuals = []

        for device, mount_point, fstype in self.virtuals:
            path = os.path.join(rootfs, './' + mount_point)
            if not os.path.exists(path):
                os.mkdir(path)
            vmdb.runcmd(['mount', '-t', fstype, device, path])
            state.virtuals.append(path)
        logging.debug('mounted virtuals: %r', state.virtuals)

    def unmount_virtuals(self, state):
        logging.debug('unmounting virtuals: %r', state.virtuals)
        for mount_point in reversed(state.virtuals):
            try:
                vmdb.unmount(mount_point)
            except vmdb.NotMounted as e:
                logging.warning(str(e))
            except cliapp.AppException:
                vmdb.warning('Something went wrong while unmounting. Ignoring.')
