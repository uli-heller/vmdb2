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

import vmdb


class AnsiblePlugin(vmdb.Plugin):
    def enable(self):
        self.app.step_runners.add(AnsibleStepRunner())


class AnsibleStepRunner(vmdb.StepRunnerInterface):
    def get_key_spec(self):
        return {"ansible": str, "playbook": str}

    def run(self, values, settings, state):
        tag = values["ansible"]
        playbook = values["playbook"]
        mount_point = state.tags.get_builder_mount_point(tag)
        rootfs_tarball = settings["rootfs-tarball"]

        state.ansible_inventory = self.create_inventory(mount_point)
        vmdb.progress(
            "Created {} for Ansible inventory".format(state.ansible_inventory)
        )

        vars_filename = self.create_vars(rootfs_tarball)
        vmdb.progress("Created {} for Ansible variables".format(vars_filename))

        env = dict(os.environ)
        env["ANSIBLE_NOCOWS"] = "1"
        vmdb.runcmd(
            [
                "ansible-playbook",
                "-c",
                "chroot",
                "-i",
                state.ansible_inventory,
                "-e",
                "@{}".format(vars_filename),
                playbook,
            ],
            env=env,
        )

    def teardown(self, values, settings, state):
        if hasattr(state, "ansible_inventory"):
            vmdb.progress("Removing {}".format(state.ansible_inventory))
            os.remove(state.ansible_inventory)

    def create_inventory(self, chroot):
        fd, filename = tempfile.mkstemp()
        os.write(fd, "[image]\n{}\n".format(chroot).encode())
        os.close(fd)
        return filename

    def create_vars(self, tarball):
        fd, filename = tempfile.mkstemp()
        os.write(fd, 'rootfs_tarball: "{}"\n'.format(tarball).encode())
        os.close(fd)
        return filename
