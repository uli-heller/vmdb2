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


class CreateFilePlugin(cliapp.Plugin):

    def enable(self):
        self.app.step_runners.add(CreateFileStepRunner())


class CreateFileStepRunner(vmdb.StepRunnerInterface):

    def get_required_keys(self):
        return ['create-file', 'contents']

    def run(self, step, settings, state):
        root = state.tags.get_builder_from_target_mount_point('/')
        newfile = step['create-file']
        contents = step['contents']
        perm = step.get('perm', 0o644)
        uid = step.get('uid', 0)
        gid = step.get('gid', 0)

        filename = '/'.join([root,newfile])

        logging.info('Creating file %s, uid %d, gid %d, perms %o' % (filename, uid, gid, perm))
        fd = open(filename, 'w')
        fd.write(contents)
        fd.close

        os.chown(filename, uid, gid)
        os.chmod(filename, perm)
