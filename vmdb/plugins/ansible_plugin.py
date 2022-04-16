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
import tempfile

import yaml

import vmdb


class AnsiblePlugin(vmdb.Plugin):
    def enable(self):
        self.app.step_runners.add(AnsibleStepRunner())


class AnsibleStepRunner(vmdb.StepRunnerInterface):
    def get_key_spec(self):
        return {
            "ansible": str,
            "playbook": str,
            "group": "image",
            "tags": "all",
            "config_file": "",
            "extra_vars": {},
        }

    def run(self, values, settings, state):
        tag = values["ansible"]
        playbook = values["playbook"]
        ansible_tags = values["tags"]
        group_name = values["group"]
        config_file = values["config_file"]
        extra_vars = values["extra_vars"]
        mount_point = state.tags.get_builder_mount_point(tag)
        rootfs_tarball = settings["rootfs-tarball"]

        inventory = self.create_inventory(mount_point, group_name)
        if not hasattr(state, "ansible_inventory"):
            state.ansible_inventory = []
        state.ansible_inventory.append(inventory)
        vmdb.progress(f"Created {inventory} for Ansible inventory")

        extra_vars["rootfs_tarball"] = rootfs_tarball
        vars_file = self.create_vars_file(extra_vars)
        if not hasattr(state, "ansible_vars_file"):
            state.ansible_vars_file = []
        state.ansible_vars_file.append(vars_file)
        vmdb.progress(f"Created {vars_file} for Ansible variables")

        env = dict(os.environ)
        env["ANSIBLE_NOCOWS"] = "1"
        if config_file:
            if os.path.exists(config_file):
                env["ANSIBLE_CONFIG"] = config_file
                vmdb.progress(f"Using Ansible config file {config_file}")
            else:
                raise RuntimeError(f"Ansible config file {config_file} does not exist")
        vmdb.runcmd(
            [
                "ansible-playbook",
                "-c",
                "chroot",
                "-i",
                inventory,
                "--tags",
                ansible_tags,
                "-e",
                f"@{vars_file}",
                playbook,
            ],
            env=env,
        )

    def teardown(self, values, settings, state):
        if hasattr(state, "ansible_vars_file"):
            self.remove(state.ansible_vars_file)
        if hasattr(state, "ansible_inventory"):
            self.remove(state.ansible_inventory)

    def remove(self, filenames):
        for filename in filenames:
            if os.path.exists(filename):
                vmdb.progress("Removing {}".format(filename))
                os.remove(filename)

    def create_inventory(self, chroot, group_name):
        fd, filename = tempfile.mkstemp()
        os.write(fd, f"[{group_name}]\n{chroot}\n".encode())
        os.close(fd)
        return filename

    def create_vars_file(self, extra_vars):
        fd, filename = tempfile.mkstemp(suffix=".yaml")
        os.write(fd, yaml.dump(extra_vars).encode())
        os.close(fd)
        return filename
