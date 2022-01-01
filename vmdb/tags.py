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


class Tags:
    def __init__(self):
        self._tags = {}
        self._tagnames = []

    def __repr__(self):  # pragma: no cover
        return repr({"tags": self._tags, "tagnames": self._tagnames})

    def get_tags(self):
        return self._tagnames

    def has_tag(self, tag):
        return tag in self._tags

    def get_dev(self, tag):
        item = self._get(tag)
        return item["dev"]

    def get_fsuuid(self, tag):
        item = self._get(tag)
        return item["fsuuid"]

    def get_luksuuid(self, tag):
        item = self._get(tag)
        return item["luksuuid"]

    def get_dm(self, tag):
        item = self._get(tag)
        return item["dm"]

    def get_builder_mount_point(self, tag):
        item = self._get(tag)
        return item["builder_mount_point"]

    def get_fstype(self, tag):
        item = self._get(tag)
        return item["fstype"]

    def get_target_mount_point(self, tag):
        item = self._get(tag)
        return item["target_mount_point"]

    def is_cached(self, tag):
        item = self._get(tag)
        return item.get("cached", False)

    def append(self, tag):
        if tag in self._tags:
            raise TagInUse(tag)
        self._tagnames.append(tag)
        self._tags[tag] = {
            "dev": None,
            "builder_mount_point": None,
            "fstype": None,
            "target_mount_point": None,
            "fsuuid": None,
            "luksuuid": None,
            "dm": None,
        }

    def set_dev(self, tag, dev):
        item = self._get(tag)
        if item["dev"] is not None:
            raise AlreadyHasDev(tag)
        item["dev"] = dev

    def set_builder_mount_point(self, tag, mount_point, cached=False):
        item = self._get(tag)
        if item["builder_mount_point"] is not None:
            raise AlreadyMounted(tag)
        item["builder_mount_point"] = mount_point
        item["cached"] = cached

    def set_fstype(self, tag, fstype):
        item = self._get(tag)
        if item["fstype"] is not None:
            raise AlreadyHasFsType(tag)
        item["fstype"] = fstype

    def set_fsuuid(self, tag, uuid):
        item = self._get(tag)
        if item["fsuuid"] is not None:
            raise AlreadyHasFsUuid(tag)
        item["fsuuid"] = uuid

    def set_luksuuid(self, tag, uuid):
        item = self._get(tag)
        if item["luksuuid"] is not None:
            raise AlreadyHasLuksUuid(tag)
        item["luksuuid"] = uuid

    def set_dm(self, tag, name):
        item = self._get(tag)
        if item["dm"] is not None:
            raise AlreadyHasDeviceMapper(tag)
        item["dm"] = name

    def set_target_mount_point(self, tag, target_mount_point):
        item = self._get(tag)
        if item["target_mount_point"] is not None:
            raise AlreadyHasTargetMountPoint(tag)
        item["target_mount_point"] = target_mount_point

    def get_builder_from_target_mount_point(self, target_mount_point):
        for item in self._tags.values():
            if item["target_mount_point"] == target_mount_point:
                return item["builder_mount_point"]
        raise NeedBothMountPoints(target_mount_point)

    def _get(self, tag):
        item = self._tags.get(tag)
        if item is None:
            raise UnknownTag(tag)
        return item


class TagInUse(Exception):
    def __init__(self, tag):
        super().__init__("Tag already used: {}".format(tag))


class UnknownTag(Exception):
    def __init__(self, tag):
        super().__init__("Unknown tag: {}".format(tag))


class AlreadyHasDev(Exception):
    def __init__(self, tag):
        super().__init__("Already has device: {}".format(tag))


class AlreadyMounted(Exception):
    def __init__(self, tag):
        super().__init__("Already mounted tag: {}".format(tag))


class AlreadyHasFsType(Exception):
    def __init__(self, tag):
        super().__init__("Already has filesytem type: {}".format(tag))


class AlreadyHasTargetMountPoint(Exception):
    def __init__(self, tag):
        super().__init__("Already has target mount point: {}".format(tag))


class AlreadyHasFsUuid(Exception):
    def __init__(self, tag):
        super().__init__("Already has fs UUID: {}".format(tag))


class AlreadyHasLuksUuid(Exception):
    def __init__(self, tag):
        super().__init__("Already has LuksUUID: {}".format(tag))


class AlreadyHasDeviceMapper(Exception):
    def __init__(self, tag):
        super().__init__("Already has device-mapper name: {}".format(tag))


class NeedBothMountPoints(Exception):
    def __init__(self, target_mp):
        super().__init__("Need both mount points set, target: {}".format(target_mp))
