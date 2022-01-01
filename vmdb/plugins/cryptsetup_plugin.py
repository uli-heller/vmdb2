# Copyright 2022  Lars Wirzenius
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
import tempfile

import vmdb


class CryptsetupPlugin(vmdb.Plugin):
    def enable(self):
        self.app.step_runners.add(CryptsetupStepRunner())


class CryptsetupStepRunner(vmdb.StepRunnerInterface):
    def get_key_spec(self):
        return {"cryptsetup": str, "password": str, "name": str}

    def run(self, step, settings, state):
        cleartext_tag = step["cryptsetup"]
        password = step["password"]
        name = step["name"]

        device = state.tags.get_dev(cleartext_tag)
        tmp = tempfile.mkdtemp()
        key = os.path.join(tmp, "key")
        with open(key, "w") as f:
            f.write(password)

        vmdb.runcmd(["cryptsetup", "luksFormat", "--batch-mode", device, key])
        vmdb.runcmd(
            ["cryptsetup", "open", "--type=luks", "--key-file", key, device, name]
        )
        crypt_device = f"/dev/mapper/{name}"
        assert os.path.exists(crypt_device)

        uuid = vmdb.runcmd(["cryptsetup", "luksUUID", device]).decode("UTF8").strip()

        state.tags.append(name)
        state.tags.set_dev(name, crypt_device)
        state.tags.set_luksuuid(name, uuid)
        state.tags.set_dm(name, name)
        vmdb.progress(f"LUKS: name={name} dev={crypt_device} luksuuid={uuid} dm={name}")
        vmdb.progress(f"LUKS: {state.tags._tags}")
        vmdb.progress("remembering LUKS device {} as {}".format(crypt_device, name))

        shutil.rmtree(tmp)
