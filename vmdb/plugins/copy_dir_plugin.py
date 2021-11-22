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

import vmdb
import os
import logging
import shutil


class CopyDirPlugin(vmdb.Plugin):
    def enable(self):
        self.app.step_runners.add(CopyDirStepRunner())


class CopyDirStepRunner(vmdb.StepRunnerInterface):
    def get_key_spec(self):
        return {
            "copy-dir": str,
            "src": str,
            "perm": 0o755,
            "umask": 0o022,
            "uid": 0,
            "gid": 0,
            "user": "",
            "group": ""
        }

    def run(self, values, settings, state):
        root = state.tags.get_builder_from_target_mount_point("/")
        newdir = values["copy-dir"]
        src = values["src"]
        perm = values["perm"]
        umask = values["umask"]

        if values["user"]:
            uid = self._get_id_from_file("/".join([root, "etc/passwd"]),
                                         values["user"])
        else:
            uid = values["uid"]

        if values["group"]:
            gid = self._get_id_from_file("/".join([root, "etc/group"]),
                                         values["group"])
        else:
            gid = values["gid"]

        tgt_dir = "/".join([root, newdir])

        # ensure src and target paths don't end with a '/'
        if src.endswith('/'):
            src = src[:-1]
        if tgt_dir.endswith('/'):
            tgt_dir = tgt_dir[:-1]

        vmdb.progress(
            "Copying dir %s to %s, uid %d, gid %d, umask %o"
            % (src, tgt_dir, uid, gid, umask)
        )

        # create missing parent dirs as required
        tgt_parent_dir = tgt_dir
        missing_parent_dirs = []
        while not os.path.exists(tgt_parent_dir):
            missing_parent_dirs.append(tgt_parent_dir)
            tgt_parent_dir = os.path.dirname(tgt_parent_dir)

        for d in reversed(missing_parent_dirs):
            self._create_dir(d, perm & ~umask, uid, gid)

        for base_dir, dirs, files in os.walk(src):
            base_tgt = base_dir.replace(src, tgt_dir)
            for dir in dirs:
                src_mode = os.stat(os.path.join(base_dir, dir)).st_mode
                umasked_mode = src_mode & ~umask
                dir_path = os.path.join(base_tgt, dir)
                if not os.path.exists(dir_path):
                    self._create_dir(dir_path, umasked_mode, uid, gid)

            for f in files:
                src_file = os.path.join(base_dir, f)
                tgt_file = os.path.join(base_tgt, f)
                src_mode = os.stat(src_file).st_mode
                umasked_mode = src_mode & ~umask
                with open(src_file, "rb") as inp:
                    with open(tgt_file, "wb") as output:
                        os.chown(tgt_file, uid, gid)
                        os.chmod(tgt_file, umasked_mode)
                        shutil.copyfileobj(inp, output)

    def _create_dir(self, dir_path, mode, uid, gid):
        os.makedirs(dir_path, mode=mode, exist_ok=True)
        os.chown(dir_path, uid, gid)

    def _get_id_from_file(self, file_path, name):
        with open(file_path) as fh:
            for line in fh:
                if line.startswith(f"{name}:"):
                    id = line.split(':', 4)[2]
                    return int(id)
        raise RuntimeError(f'Failed to find entry for "{name}" in {file_path}')