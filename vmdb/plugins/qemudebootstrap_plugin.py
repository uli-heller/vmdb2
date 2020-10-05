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


import vmdb


class QemuDebootstrapPlugin(vmdb.Plugin):
    def enable(self):
        self.app.step_runners.add(QemuDebootstrapStepRunner())


class QemuDebootstrapStepRunner(vmdb.StepRunnerInterface):
    def get_key_spec(self):
        return {
            "qemu-debootstrap": str,
            "target": str,
            "mirror": str,
            "arch": str,
            "keyring": "",
            "variant": "-",
            "components": ["main"],
        }

    def run(self, values, settings, state):
        suite = values["qemu-debootstrap"]
        tag = values["target"]
        target = state.tags.get_builder_mount_point(tag)
        mirror = values["mirror"]
        keyring = values["keyring"] or None
        variant = values["variant"]
        arch = values["arch"]
        components = values["components"]
        if not (suite and tag and target and mirror and arch):
            raise Exception("missing arg for qemu-debootstrap step")
        # Update the state with the target architecture declared here
        # in order that later stages can find it and behave
        # appropriately.
        state.arch = arch
        if keyring:
            vmdb.runcmd(
                [
                    "qemu-debootstrap",
                    "--keyring",
                    keyring,
                    "--arch",
                    arch,
                    "--variant",
                    variant,
                    "--components",
                    ",".join(components),
                    suite,
                    target,
                    mirror,
                ]
            )
        else:
            vmdb.runcmd(
                [
                    "qemu-debootstrap",
                    "--arch",
                    arch,
                    "--variant",
                    variant,
                    "--components",
                    ",".join(components),
                    suite,
                    target,
                    mirror,
                ]
            )
        vmdb.runcmd_chroot(target, ["apt-get", "update"])

    def run_even_if_skipped(self, values, settings, state):
        tag = values["target"]
        target = state.tags.get_builder_mount_point(tag)
        state.arch = values["arch"]
        vmdb.runcmd_chroot(target, ["apt-get", "update"])
