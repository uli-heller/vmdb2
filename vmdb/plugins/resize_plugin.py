# Copyright 2020  Lars Wirzenius, Peter Lawler
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

import vmdb


SCRIPT = """\
#!/bin/sh

rootpart="$(findmnt -n -o SOURCE /)"
rootdev="/dev/$(lsblk -no pkname "$rootpart")"
partno="$(lsblk -n --list "$rootpart" | wc -l)"

flock $rootdev sfdisk -f $rootdev -N "$partno" <<EOF
,+
EOF

sleep 5

udevadm settle

sleep 5

flock $rootdev partprobe $rootdev

mount -o remount,rw $rootpart

resize2fs -f $rootpart

exit 0
"""

SERVICE = """\
[Unit]
Description=resize root file system
Before=local-fs-pre.target
DefaultDependencies=no

[Service]
Type=oneshot
TimeoutSec=infinity
ExecStart=/usr/sbin/resize-rootfs
ExecStart=/bin/systemctl --no-reload disable %n

[Install]
RequiredBy=local-fs-pre.target
"""


class ResizeRootfsPlugin(vmdb.Plugin):
    def enable(self):
        self.app.step_runners.add(ResizeRootfsStepRunner())


class ResizeRootfsStepRunner(vmdb.StepRunnerInterface):
    def get_key_spec(self):
        return {"resize-rootfs": str}

    def run(self, values, settings, state):
        tag = values["resize-rootfs"]
        root = state.tags.get_builder_mount_point(tag)

        partprobe = self.relative(root, "/sbin/parted")
        if not os.path.exists(partprobe):
            raise Exception("partprobe is not installed on image, can't resize")

        script_path = "/usr/sbin/resize-rootfs"
        service_path = "/etc/systemd/system/resize-rootfs.service"
        requires_path = "/etc/systemd/system/systemd-remount-fs.service.requires/"

        # Install the script that actually does the resizing.
        self.install(SCRIPT, root, script_path, 0o755)

        # Install the systemd service file to invoke the script at boot.
        self.install(SERVICE, root, service_path, 0o644)

        # Tell systemd to run the script at the right time. This corresponds to
        # "systemctl enable".
        self.mkdir(root, "etc/systemd/system/systemd-remount-fs.service.requires")
        self.symlink(root, service_path, requires_path)

    def relative(self, root, pathname):
        return os.path.join(root, "./" + pathname)

    def install(self, content, root, filename, mode):
        filename = self.relative(root, filename)
        with open(filename, "w") as f:
            f.write(content)
        os.chmod(filename, mode)

    def mkdir(self, root, pathname):
        pathname = self.relative(root, pathname)
        os.makedirs(pathname, exist_ok=True)

    def symlink(self, root, linkto, linkname):
        linkname = self.relative(root, linkname)
        basename = os.path.basename(linkto)
        linkname = os.path.join(linkname, basename)
        os.symlink(linkto, linkname)
