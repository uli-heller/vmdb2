# Copyright 2018  Lars Wirzenius
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
import tempfile

import vmdb


class LuksPlugin(vmdb.Plugin):
    def enable(self):
        self.app.step_runners.add(CryptsetupStepRunner())


class CryptsetupStepRunner(vmdb.StepRunnerInterface):
    def get_key_spec(self):
        return {"cryptsetup": str, "tag": str, "key-file": "", "key-cmd": ""}

    def run(self, values, settings, state):
        underlying = values["cryptsetup"]
        crypt_name = values["tag"]

        if not isinstance(underlying, str):
            raise vmdb.NotString("cryptsetup", underlying)
        if not isinstance(crypt_name, str):
            raise vmdb.NotString("cryptsetup: tag", crypt_name)

        state.tmp_key_file = None
        key_file = values["key-file"] or None
        key_cmd = values["key-cmd"] or None
        if key_file is None and key_cmd is None:
            raise Exception("cryptsetup step MUST define one of key-file or key-cmd")

        if key_file is None:
            output = vmdb.runcmd(["sh", "-ec", key_cmd])
            output = output.decode("UTF-8")
            key = output.splitlines()[0]
            fd, key_file = tempfile.mkstemp()
            state.tmp_key_file = key_file
            os.close(fd)
            open(key_file, "w").write(key)

        dev = state.tags.get_dev(underlying)
        if dev is None:
            for t in state.tags.get_tags():
                logging.debug(
                    "tag %r dev %r mp %r",
                    t,
                    state.tags.get_dev(t),
                    state.tags.get_builder_mount_point(t),
                )
            assert 0

        vmdb.runcmd(["cryptsetup", "-q", "luksFormat", dev, key_file])
        vmdb.runcmd(
            [
                "cryptsetup",
                "open",
                "--type",
                "luks2",
                "--key-file",
                "--allow-discards",
                key_file,
                dev,
                crypt_name,
            ]
        )

        crypt_dev = "/dev/mapper/{}".format(crypt_name)
        assert os.path.exists(crypt_dev)
        state.tags.append(crypt_name)
        state.tags.set_dev(crypt_name, crypt_dev)

    def teardown(self, values, settings, state):
        x = state.tmp_key_file
        if x is not None and os.path.exists(x):
            os.remove(x)

        crypt_name = values["tag"]

        crypt_dev = "/dev/mapper/{}".format(crypt_name)
        vmdb.runcmd(["cryptsetup", "close", crypt_dev])
