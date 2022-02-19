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

import os
import shutil
import subprocess

import vmdb


class DebootstrapPlugin(vmdb.Plugin):
    def enable(self):
        self.app.step_runners.add(DebootstrapStepRunner())


class DebootstrapStepRunner(vmdb.StepRunnerInterface):
    def get_key_spec(self):
        return {
            "debootstrap": str,
            "target": str,
            "mirror": str,
            "arch": "",
            "keyring": "",
            "install_keyring": False,
            "variant": "-",
            "components": ["main"],
            "include": [],
            "require_empty_target": True,
        }

    def run(self, values, settings, state):
        suite = values["debootstrap"]
        tag = values["target"]
        target = state.tags.get_builder_mount_point(tag)
        mirror = values["mirror"]
        keyring = values["keyring"] or None
        install_keyring = values["install_keyring"]
        include = values["include"]
        require_empty = values["require_empty_target"]
        arch = (
            values["arch"]
            or subprocess.check_output(["dpkg", "--print-architecture"]).strip()
        )
        variant = values["variant"]
        components = values["components"]

        if not (suite and tag and target and mirror):
            raise Exception("missing arg for debootstrap step")

        if os.path.exists(target) and require_empty:
            allowed_names = ["lost+found"]
            names = [n for n in os.listdir(target) if n not in allowed_names]
            if len(names) > 0:
                raise Exception(
                    f"debootstrap target {target} is a not an empty directory: {names}"
                )

        cmd = [
            "debootstrap",
            "--arch",
            arch,
            "--variant",
            variant,
            "--components",
            ",".join(components),
        ]

        remove_pkgs = []
        if keyring:
            cmd.extend(["--keyring", keyring])
            if install_keyring and "gnupg" not in include:
                include.append("gnupg")
                # If gnupg needed to be installed it should be removed again to
                # minimize the installation footprint
                remove_pkgs.append("gnupg")

        if include:
            cmd.extend(["--include", ",".join(include)])

        cmd.extend([suite, target, mirror])

        vmdb.runcmd(cmd)

        if keyring and install_keyring:
            keyring_basename = os.path.basename(keyring)
            chroot_keyring = os.path.join(target, keyring_basename)
            shutil.copyfile(keyring, os.path.join(target, keyring_basename))
            vmdb.runcmd_chroot(target, ["apt-key", "add", f"/{keyring_basename}"])
            os.remove(chroot_keyring)

        if remove_pkgs:
            vmdb.runcmd_chroot(
                target,
                [
                    "apt-get",
                    "remove",
                    "--purge",
                    "-y",
                ]
                + remove_pkgs,
            )
