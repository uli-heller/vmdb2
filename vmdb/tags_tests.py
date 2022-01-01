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


import unittest


import vmdb


class TagsTests(unittest.TestCase):
    def test_lists_no_tags_initially(self):
        tags = vmdb.Tags()
        self.assertEqual(tags.get_tags(), [])

    def test_tells_if_tag_exists(self):
        tags = vmdb.Tags()
        self.assertFalse(tags.has_tag("foo"))
        tags.append("foo")
        self.assertTrue(tags.has_tag("foo"))
        self.assertEqual(tags.get_tags(), ["foo"])

    def test_remembers_order(self):
        tags = vmdb.Tags()
        tags.append("foo")
        tags.append("bar")
        self.assertTrue(tags.get_tags(), ["foo", "bar"])

    def test_get_dev_raises_error_for_unknown_tag(self):
        tags = vmdb.Tags()
        with self.assertRaises(vmdb.UnknownTag):
            tags.get_dev("does-not-exist")

    def test_getting_builder_mount_point_raises_error_for_unknown_tag(self):
        tags = vmdb.Tags()
        with self.assertRaises(vmdb.UnknownTag):
            tags.get_builder_mount_point("does-not-exist")

    def test_raises_error_for_reused_tag(self):
        tags = vmdb.Tags()
        tags.append("tag")
        with self.assertRaises(vmdb.TagInUse):
            tags.append("tag")

    def test_sets_dev(self):
        tags = vmdb.Tags()
        tags.append("first")
        tags.set_dev("first", "/dev/foo")
        self.assertEqual(tags.get_tags(), ["first"])
        self.assertEqual(tags.get_dev("first"), "/dev/foo")
        self.assertEqual(tags.get_builder_mount_point("first"), None)

    def test_adds_builder_mount_point(self):
        tags = vmdb.Tags()
        tags.append("first")
        tags.set_builder_mount_point("first", "/mnt/foo")
        self.assertEqual(tags.get_tags(), ["first"])
        self.assertEqual(tags.get_dev("first"), None)
        self.assertEqual(tags.get_builder_mount_point("first"), "/mnt/foo")

    def test_builder_mount_point_is_uncached_by_default(self):
        tags = vmdb.Tags()
        tags.append("first")
        tags.set_builder_mount_point("first", "/mnt/foo")
        self.assertFalse(tags.is_cached("first"))

    def test_builder_mount_point_can_be_made_cached(self):
        tags = vmdb.Tags()
        tags.append("first")
        tags.set_builder_mount_point("first", "/mnt/foo", cached=True)
        self.assertTrue(tags.is_cached("first"))

    def test_set_dev_raises_error_for_unknown_tag(self):
        tags = vmdb.Tags()
        with self.assertRaises(vmdb.UnknownTag):
            tags.set_dev("first", "/mnt/foo")

    def test_set_builder_mount_point_raises_error_for_unknown_tag(self):
        tags = vmdb.Tags()
        with self.assertRaises(vmdb.UnknownTag):
            tags.set_builder_mount_point("first", "/mnt/foo")

    def test_set_builder_mount_point_raises_error_for_double_mount(self):
        tags = vmdb.Tags()
        tags.append("first")
        tags.set_builder_mount_point("first", "/mnt/foo")
        with self.assertRaises(vmdb.AlreadyMounted):
            tags.set_builder_mount_point("first", "/mnt/foo")

    def test_set_dev_raises_error_for_double_dev(self):
        tags = vmdb.Tags()
        tags.append("first")
        tags.set_dev("first", "/dev/foo")
        with self.assertRaises(vmdb.AlreadyHasDev):
            tags.set_dev("first", "/dev/foo")

    def test_set_fstype(self):
        tags = vmdb.Tags()
        tags.append("first")
        tags.set_fstype("first", "ext4")
        self.assertEqual(tags.get_fstype("first"), "ext4")

    def test_set_fstype_raises_error_for_double_fstype(self):
        tags = vmdb.Tags()
        tags.append("first")
        tags.set_fstype("first", "ext3")
        with self.assertRaises(vmdb.AlreadyHasFsType):
            tags.set_fstype("first", "ext4")

    def test_set_fsuuid(self):
        tags = vmdb.Tags()
        tags.append("first")
        tags.set_fsuuid("first", "uuid")
        self.assertEqual(tags.get_fsuuid("first"), "uuid")

    def test_set_fsuuid_raises_error_for_double_fstype(self):
        tags = vmdb.Tags()
        tags.append("first")
        tags.set_fsuuid("first", "uuid")
        with self.assertRaises(vmdb.AlreadyHasFsUuid):
            tags.set_fsuuid("first", "other")

    def test_set_luksuuid(self):
        tags = vmdb.Tags()
        tags.append("first")
        tags.set_luksuuid("first", "uuid")
        self.assertEqual(tags.get_luksuuid("first"), "uuid")

    def test_set_luksuuid_raises_error_for_double_fstype(self):
        tags = vmdb.Tags()
        tags.append("first")
        tags.set_luksuuid("first", "uuid")
        with self.assertRaises(vmdb.AlreadyHasLuksUuid):
            tags.set_luksuuid("first", "other")

    def test_set_dm(self):
        tags = vmdb.Tags()
        tags.append("first")
        tags.set_dm("first", "dm")
        self.assertEqual(tags.get_dm("first"), "dm")

    def test_set_dm_raises_error_for_double_fstype(self):
        tags = vmdb.Tags()
        tags.append("first")
        tags.set_dm("first", "dm")
        with self.assertRaises(vmdb.AlreadyHasDeviceMapper):
            tags.set_dm("first", "other")

    def test_set_target_mount_point(self):
        tags = vmdb.Tags()
        tags.append("first")
        tags.set_target_mount_point("first", "/boot")
        self.assertEqual(tags.get_target_mount_point("first"), "/boot")

    def test_set_target_mount_point_raises_error_for_double_target_mount_point(self):
        tags = vmdb.Tags()
        tags.append("first")
        tags.set_target_mount_point("first", "/boot")
        with self.assertRaises(vmdb.AlreadyHasTargetMountPoint):
            tags.set_target_mount_point("first", "/")

    def test_raises_error_if_both_mount_points_not_set(self):
        tags = vmdb.Tags()
        tags.append("first")
        tags.set_target_mount_point("first", "/boot")
        with self.assertRaises(vmdb.NeedBothMountPoints):
            tags.get_builder_from_target_mount_point("/")

    def test_returns_builder_when_given_target_mount_point(self):
        tags = vmdb.Tags()
        tags.append("first")
        tags.set_builder_mount_point("first", "/mnt/foo")
        tags.set_target_mount_point("first", "/boot")
        self.assertEqual(tags.get_builder_from_target_mount_point("/boot"), "/mnt/foo")
