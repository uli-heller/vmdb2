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


class DebootstrapPlugin(cliapp.Plugin):
    def enable(self):
        self.app.step_runners.add(DebootstrapStepRunner())


class DebootstrapStepRunner(vmdb.StepRunnerInterface):
    def get_key_spec(self):
        return {
            "debootstrap": str,
            "target": str,
            "mirror": str,
            "keyring": "",
            "variant": "-",
        }

    def run(self, values, settings, state):
        suite = values["debootstrap"]
        tag = values["target"]
        target = state.tags.get_builder_mount_point(tag)
        mirror = values["mirror"]
        keyring = values["keyring"] or None
        variant = values["variant"]

        if not (suite and tag and target and mirror):
            raise Exception("missing arg for debootstrap step")
        if keyring:
            vmdb.runcmd(
                [
                    "debootstrap",
                    "--keyring",
                    keyring,
                    "--variant",
                    variant,
                    suite,
                    target,
                    mirror,
                ]
            )
        else:
            vmdb.runcmd(["debootstrap", "--variant", variant, suite, target, mirror])

    def run_even_if_skipped(self, values, settings, state):
        tag = values["target"]
        target = state.tags.get_builder_mount_point(tag)
        vmdb.runcmd_chroot(target, ["apt-get", "update"])
