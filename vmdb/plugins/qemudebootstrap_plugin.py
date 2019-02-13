# Copyright 2017  Lars Wirzenius and Stuart Prescott
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


class QemuDebootstrapPlugin(cliapp.Plugin):

    def enable(self):
        self.app.step_runners.add(QemuDebootstrapStepRunner())


class QemuDebootstrapStepRunner(vmdb.StepRunnerInterface):

    def get_required_keys(self):
        return ['qemu-debootstrap', 'target', 'mirror', 'arch']

    def run(self, step, settings, state):
        suite = step['qemu-debootstrap']
        tag = step['target']
        target = state.tags.get_mount_point(tag)
        mirror = step['mirror']
        variant = step.get('variant', '-')
        arch = step['arch']
        components = step.get('components', ['main'])
        if not (suite and tag and target and mirror and arch):
            raise Exception('missing arg for qemu-debootstrap step')
        vmdb.runcmd(
            ['qemu-debootstrap',
             '--arch', arch,
             '--variant', variant,
             '--components', ','.join(components), suite,
             target,
             mirror])
        vmdb.runcmd_chroot(target, ['apt-get', 'update'])

    def run_even_if_skipped(self, step, settings, state):
        tag = step['target']
        target = state.tags.get_mount_point(tag)
        vmdb.runcmd_chroot(target, ['apt-get', 'update'])
