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


import unittest

import vmdb


class StepRunnerListTests(unittest.TestCase):
    def test_is_empty_initially(self):
        steps = vmdb.StepRunnerList()
        self.assertEqual(len(steps), 0)

    def test_adds_a_runner(self):
        steps = vmdb.StepRunnerList()
        runner = DummyStepRunner()
        steps.add(runner)
        self.assertEqual(len(steps), 1)

    def test_finds_correct_runner(self):
        steps = vmdb.StepRunnerList()
        keyspec = {"foo": str, "bar": str}
        runner = DummyStepRunner(keyspec=keyspec)
        steps.add(runner)
        found = steps.find({"foo": "foo", "bar": "bar"})
        self.assertEqual(runner, found)

    def test_raises_error_if_runner_not_found(self):
        steps = vmdb.StepRunnerList()
        keyspec = {"foo": str, "bar": str}
        runner = DummyStepRunner(keyspec=keyspec)
        steps.add(runner)
        with self.assertRaises(vmdb.NoMatchingRunner):
            steps.find({"foo": "foo"})

    def test_raises_error_if_wrong_step_key_values(self):
        steps = vmdb.StepRunnerList()
        keyspec = {"foo": str}
        runner = DummyStepRunner(keyspec=keyspec)
        steps.add(runner)
        with self.assertRaises(vmdb.StepKeyWrongValueType):
            steps.find({"foo": 42})


class DummyStepRunner(vmdb.StepRunnerInterface):
    def __init__(self, keyspec=None):
        self.keyspec = keyspec

    def get_key_spec(self):
        return self.keyspec

    def run(self, *args):
        pass


class StepRunnerGetKeyValuesTests(unittest.TestCase):
    def test_returns_values_from_step_for_mandatory_keys(self):
        keyspec = {"foo": str}
        runner = DummyStepRunner(keyspec=keyspec)
        self.assertEqual(runner.get_values({"foo": "bar"}), {"foo": "bar"})

    def test_raises_error_for_missing_mandatory_key(self):
        keyspec = {"foo": str}
        runner = DummyStepRunner(keyspec=keyspec)
        with self.assertRaises(vmdb.StepKeyMissing):
            runner.get_values({})

    def test_raises_error_for_wrong_type_of_value_for_mandatory_key(self):
        keyspec = {"foo": str}
        runner = DummyStepRunner(keyspec=keyspec)
        with self.assertRaises(vmdb.StepKeyWrongValueType):
            runner.get_values({"foo": 42})

    def test_returns_default_value_for_missing_optional_key(self):
        keyspec = {"foo": "bar"}
        runner = DummyStepRunner(keyspec=keyspec)
        self.assertEqual(runner.get_values({}), {"foo": "bar"})

    def test_returns_actual_value_for_optional_key(self):
        keyspec = {"foo": "bar"}
        runner = DummyStepRunner(keyspec=keyspec)
        self.assertEqual(runner.get_values({"foo": "yo"}), {"foo": "yo"})

    def test_raises_error_for_wrong_type_of_value_for_optional_key(self):
        keyspec = {"foo": "bar"}
        runner = DummyStepRunner(keyspec=keyspec)
        with self.assertRaises(vmdb.StepKeyWrongValueType):
            runner.get_values({"foo": 42})
