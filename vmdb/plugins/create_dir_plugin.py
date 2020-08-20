# Copyright 2019 Gunnar Wolf
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
import os
import logging


class CreateDirPlugin(cliapp.Plugin):
    def enable(self):
        self.app.step_runners.add(CreateDirStepRunner())


class CreateDirStepRunner(vmdb.StepRunnerInterface):
    def get_key_spec(self):
        return {"create-dir": str, "perm": 0o755, "uid": 0, "gid": 0}

    def run(self, values, settings, state):
        root = state.tags.get_builder_from_target_mount_point("/")
        newdir = values["create-dir"]
        path = "/".join([root, newdir])
        perm = values["perm"]
        uid = values["uid"]
        gid = values["gid"]

        logging.info(
            "Creating directory %s, uid %d, gid %d, perms %o" % (path, uid, gid, perm)
        )

        os.makedirs(path, perm)
        os.chown(path, uid, gid)
