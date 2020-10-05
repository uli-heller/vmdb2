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


import argparse
import logging
import os
import sys

import vmdb


class Vmdb2:
    def __init__(self, version):
        self._version = version

    def run(self):
        args = self.parse_command_line()
        vmdb.set_verbose_progress(args.verbose)
        tvars = self.template_vars_from_args(args)

        cmd = None
        if args.version:
            cmd = VersionCommand(self._version)
        elif args.image or args.output:
            if args.image:
                cmd = ReuseImageCommand(args.image, args.specfile, args.rootfs_tarball)
            else:
                cmd = NewImageCommand(args.output, args.specfile, args.rootfs_tarball)
            builder = cmd.builder()
            builder.add_template_vars(tvars)

        if cmd is None:
            sys.exit("I don't know what to do, re-run with --help")

        if args.log:
            self.setup_logging(args.log)
            self.log_startup()
        try:
            cmd.run()
        except Exception as e:
            logging.error(f"ERROR: {e}", exc_info=True)
            sys.exit(f"ERROR: {e}\n")
        logging.debug("Ending, all OK")

    def parse_command_line(self):
        p = argparse.ArgumentParser(
            description="build disk images with Debian installed"
        )

        p.add_argument("--image", metavar="FILE")
        p.add_argument("--output", metavar="FILE")
        p.add_argument("--rootfs-tarball", metavar="FILE")
        p.add_argument("-v", "--verbose", action="store_true")
        p.add_argument("--log")
        p.add_argument("--version", action="store_true")
        p.add_argument("specfile")

        return p.parse_args()

    def setup_logging(self, filename):
        fmt = "%(asctime)s %(levelname)s %(message)s"
        datefmt = "%Y-%m-%d %H:%M:%S"
        formatter = logging.Formatter(fmt, datefmt)

        handler = logging.FileHandler(filename)
        handler.setFormatter(formatter)

        logger = logging.getLogger()
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)

    def log_startup(self):
        logging.info(f"Starting vmdb2 version {self._version}")

    def template_vars_from_args(self, args):
        return {
            "image": args.image,
            "output": args.output,
            "rootfs_tarball": args.rootfs_tarball,
        }


class Command:
    def run(self):
        raise NotImplementedError()


class VersionCommand(Command):
    def __init__(self, version):
        self.version = version

    def run(self):
        sys.stdout.write("{}\n".format(self.version))


class NewImageCommand(Command):
    def __init__(self, filename, specfile, tarball):
        self._builder = ImageBuilder(filename, specfile, tarball)

    def builder(self):
        return self._builder

    def run(self):
        # FIXME: create file
        self._builder.build()


class ReuseImageCommand(Command):
    def __init__(self, filename, specfile, tarball):
        self._builder = ImageBuilder(filename, specfile, tarball)

    def builder(self):
        return self._builder

    def run(self):
        self._builder.build()


class ImageBuilder:
    def __init__(self, filename, specfile, tarball):
        self._filename = filename
        self._specfile = specfile
        self._tarball = tarball
        self._tvars = {}

    def add_template_vars(self, tvars):
        self._tvars.update(tvars)

    def build(self):
        spec = self.load_spec_file(self._specfile)
        state = vmdb.State()
        state.tags = vmdb.Tags()
        state.arch = vmdb.runcmd(["dpkg", "--print-architecture"]).decode("UTF-8").strip()
        self.add_template_vars(state.as_dict())
        steps = spec.get_steps(self._tvars)

        # Check that we have step runners for each step
        self.load_step_runners()
        for step in steps:
            self.step_runners.find(step)

        steps_taken, core_meltdown = self.run_steps(steps, state)
        if core_meltdown:
            vmdb.progress("Something went wrong, cleaning up!")
            self.run_teardowns(steps_taken, state)
        else:
            self.run_teardowns(steps_taken, state)
            vmdb.progress("All went fine.")

        if core_meltdown:
            logging.error("An error occurred, exiting")
            sys.exit(1)

    def load_spec_file(self, filename):
        spec = vmdb.Spec()
        if filename == "-":
            vmdb.progress("Load spec from stdin")
            spec.load_file(sys.stdin)
        else:
            vmdb.progress("Load spec file {}".format(filename))
            with open(filename) as f:
                spec.load_file(f)
        return spec

    def load_step_runners(self):
        self.step_runners = vmdb.StepRunnerList()
        plugindir = os.path.join(os.path.dirname(vmdb.__file__), "plugins")
        for klass in vmdb.find_plugins(plugindir, "Plugin"):
            klass(self).enable()

    def run_steps(self, steps, state):
        return self.run_steps_helper(steps, state, "Running step: %r", "run", False)

    def run_teardowns(self, steps, state):
        return self.run_steps_helper(
            list(reversed(steps)), state, "Running teardown: %r", "teardown", True
        )

    def run_steps_helper(self, steps, state, msg, method_name, keep_going):
        core_meltdown = False
        steps_taken = []
        settings = {"rootfs-tarball": self._tarball}

        even_if_skipped = method_name + "_even_if_skipped"
        for step in steps:
            try:
                logging.info(msg, step)
                steps_taken.append(step)
                runner = self.step_runners.find(step)
                if runner.skip(step, settings, state):
                    logging.info("Skipping as requested by unless")
                    method_names = [even_if_skipped]
                else:
                    method_names = [method_name, even_if_skipped]

                methods = [
                    getattr(runner, name)
                    for name in method_names
                    if hasattr(runner, name)
                ]

                values = runner.get_values(step)
                for method in methods:
                    logging.info("Calling %s", method)
                    method(values, settings, state)
            except KeyError as e:
                vmdb.error("Key error: %s" % str(e))
                vmdb.error(repr(e))
                core_meltdown = True
                if not keep_going:
                    break
            except BaseException as e:
                vmdb.error(str(e))
                vmdb.error(repr(e))
                core_meltdown = True
                if not keep_going:
                    break

        return steps_taken, core_meltdown
