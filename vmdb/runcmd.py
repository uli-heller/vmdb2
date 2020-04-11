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


import logging
import os
import subprocess
import sys

import cliapp


_verbose = False


def set_verbose_progress(verbose):
    global _verbose
    _verbose = verbose


def error(msg):
    logging.error(msg, exc_info=True)
    sys.stderr.write('ERROR: {}\n'.format(msg))


def progress(msg):
    logging.info(msg)
    if _verbose:
        sys.stdout.write('{}\n'.format(msg))


def runcmd(argv, *argvs, **kwargs):
    progress('Exec: %r' % (argv,))
    kwargs['stdout_callback'] = _log_stdout
    kwargs['stderr_callback'] = _log_stderr
    env = kwargs.get('env', os.environ.copy())
    env['LC_ALL'] = 'C'
    kwargs['env'] = env
    return cliapp.runcmd(argv, *argvs, **kwargs)


def runcmd_chroot(chroot, argv, *argvs, **kwargs):
    full_argv = ['chroot', chroot] + argv
    return runcmd(full_argv, *argvs, **kwargs)


def _procdir(chroot):
    proc = os.path.join(chroot, 'proc')
    if not os.path.exists(proc):
        os.mkdir(proc, mode=Oo755)
    return proc


def _log_stdout(data):
    logging.debug('STDOUT: %r', data)
    return data


def _log_stderr(data):
    logging.debug('STDERR: %r', data)
    return data
