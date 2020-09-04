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


import vmdb


class KpartxPlugin(vmdb.Plugin):
    def enable(self):
        self.app.step_runners.add(KpartxStepRunner())


class KpartxStepRunner(vmdb.StepRunnerInterface):
    def get_key_spec(self):
        return {"kpartx": str}

    def run(self, values, settings, state):
        device = values["kpartx"]
        tags = state.tags.get_tags()
        devs = self.kpartx(device)
        for tag, dev in zip(tags, devs):
            vmdb.progress("remembering {} as {}".format(dev, tag))
            state.tags.set_dev(tag, dev)

    def kpartx(self, device):
        output = vmdb.runcmd(["kpartx", "-asv", device]).decode("UTF-8")
        for line in output.splitlines():
            words = line.split()
            if words[0] == "add":
                name = words[2]
                yield "/dev/mapper/{}".format(name)

    def teardown(self, values, settings, state):
        device = values["kpartx"]
        vmdb.runcmd(["kpartx", "-dsv", device])
