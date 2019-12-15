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
        self.app.step_runners.add(CreateDirStepRunner())
        self.app.step_runners.add(CreateFileStepRunner())
        self.app.step_runners.add(CopyFileStepRunner())


class CreateFileStepRunner(vmdb.StepRunnerInterface):

    def get_required_keys(self):
        return ['create-file', 'contents']

    def run(self, step, settings, state):
        root = state.tags.get_mount_point('/')
        newfile = step['create-file']
        contents = step['contents']
        perm = step.get('perm')
        uid = step.get('uid')
        gid = step.get('gid')

        filename = '/'.join([root,newfile])

        if perm:
            perm = int(perm, 8)
        else:
            perm = 0o0644
        if uid:
            uid = int(uid)
        else:
            uid = 0
        if gid:
            gid = int(gid)
        else:
            gid = 0

        logging.info('Creating file %s, uid %d, gid %d, perms %o' % (filename, uid, gid, perm))
        fd = open(filename, 'w')
        fd.write(contents)
        fd.close

        os.chown(filename, uid, gid)
        os.chmod(filename, perm)


class CopyFileStepRunner(vmdb.StepRunnerInterface):

    def get_required_keys(self):
        return ['copy-file', 'src']

    def run(self, step, settings, state):
        root = state.tags.get_mount_point('/')
        newfile = step['copy-file']
        src = step['src']
        perm = step.get('perm')
        uid = step.get('uid')
        gid = step.get('gid')

        filename = '/'.join([root,newfile])

        if perm:
            perm = int(perm, 8)
        else:
            perm = 0o0644
        if uid:
            uid = int(uid)
        else:
            uid = 0
        if gid:
            gid = int(gid)
        else:
            gid = 0

        logging.info(
            'Copying file %s to %s, uid %d, gid %d, perms %o' % (
                src, filename, uid, gid, perm))

        dirname = os.path.dirname(filename)
        os.makedirs(dirname, mode=0o511, exist_ok=True)
        with open(src, 'rb') as inp:
            with open(filename, 'wb') as output:
                contents = inp.read()
                output.write(contents)

        os.chown(filename, uid, gid)
        os.chmod(filename, perm)


class CreateDirStepRunner(vmdb.StepRunnerInterface):

    def get_required_keys(self):
        return ['create-dir']

    def run(self, step, settings, state):
        root = state.tags.get_mount_point('/')
        newdir = step['create-dir']
        path = '/'.join([root, newdir])
        perm = step.get('perm')
        uid = step.get('uid')
        gid = step.get('gid')

        if perm:
            perm = int(perm, 8)
        else:
            perm = 0o0755
        if uid:
            uid = int(uid)
        else:
            uid = 0
        if gid:
            gid = int(gid)
        else:
            gid = 0

        logging.info('Creating directory %s, uid %d, gid %d, perms %o' % (path, uid, gid, perm))

        os.makedirs(path, perm)
        os.chown(path, uid, gid)
