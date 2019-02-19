# Copyright 2019 Antonio Terceiro
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


class FstabPlugin(cliapp.Plugin):

    def enable(self):
        self.app.step_runners.add(FstabStepRunner())


class FstabStepRunner(vmdb.StepRunnerInterface):

    def get_required_keys(self):
        return ['fstab']

    def run(self, step, setting, state):
        tag = step['fstab']
        chroot = state.tags.get_mount_point(tag)

        filesystems = []

        for tag in state.tags.get_tags():
            device = state.tags.get_dev(tag)
            mount_point = state.tags.get_target_mount_point(tag)
            fstype = state.tags.get_fstype(tag)
            output = vmdb.runcmd(['blkid', '-c', '/dev/null', '-o', 'value', '-s', 'UUID', device])
            if output:
                uuid = output.decode().strip()
                filesystems.append({
                    'uuid': uuid,
                    'mount_point': mount_point,
                    'fstype': fstype,
                })
            else:
                raise Exception('Unknown UUID for device {} (to be mounted on {})'.format(device, mount_point))

        fstab_path = os.path.join(chroot, 'etc/fstab')
        line = "UUID={uuid} {mount_point} {fstype} errors=remount-ro 0 1\n"
        with open(fstab_path, 'w') as fstab:
            for entry in filesystems:
                fstab.write(line.format(**entry))
