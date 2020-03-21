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


import cliapp


class StepRunnerInterface:  # pragma: no cover

    def get_key_spec(self):
        raise NotImplementedError()

    def get_values(self, step):
        keyspec = self.get_key_spec()
        values = {}

        # Get keys from step or defaults from spec.
        for key, specvalue in keyspec.items():
            if specvalue.__class__ == type:
                if key not in step:
                    raise StepKeyMissing(key)
                values[key] = step[key]
            else:
                values[key] = step.get(key, specvalue)

        # Check types of values.
        for key, specvalue in keyspec.items():
            if specvalue.__class__ == type:
                wanted = specvalue
            else:
                wanted = specvalue.__class__
            if not isinstance(values[key], wanted):
                raise StepKeyWrongValueType(key, wanted, values[key])

        return values

    def get_required_keys(self):
        return [
            key
            for key, value in self.get_key_spec().items()
            if value.__class__ == type
        ]

    def run(self, step_spec, settings, state):
        raise NotImplementedError()

    def run_even_if_skipped(self, step_spec, settings, state):
        pass

    def teardown(self, step_spec, settings, state):
        # Default implementation does nop, so that sub-classes don't
        # need to have a nop teardown.
        pass

    def skip(self, step_spec, settings, state):
        # Return true if step should be skipped and not run. Does not
        # apply to teardowns.

        # Skipping is indicated by the step having a field 'unless',
        # which is either the name of a variable (field in state), or
        # a list of such names. If all variables have a value that
        # evaluates as truth, the step is skipped.

        value = step_spec.get('unless', None)
        if value is None:
            return False

        if isinstance(value, list):
            return all(getattr(state, field, False) for field in value)
        return getattr(state, value, False)


class StepRunnerList:

    def __init__(self):
        self._runners = []

    def __len__(self):
        return len(self._runners)

    def add(self, runner):
        self._runners.append(runner)

    def find(self, step_spec):
        actual = set(step_spec.keys())
        for runner in self._runners:
            required = set(runner.get_required_keys())
            if actual.intersection(required) == required:
                runner.get_values(step_spec)
                return runner
        raise NoMatchingRunner(actual)


class StepError(cliapp.AppException):

    def __init__(self, msg):
        logging.error(msg)
        super().__init__(msg)


class StepKeyMissing(StepError):

    def __init__(self, key):
        super().__init__('Step is missing key {}'.format(key))


class StepKeyWrongValueType(StepError):

    def __init__(self, key, wanted, actual):
        super().__init__(
            'Step key {} has value {!r}, expected {!r}'.format(
                key, wanted, actual))


class NoMatchingRunner(StepError):

    def __init__(self, keys):
        super().__init__(
            'No runner implements step with keys {}'.format(', '.join(keys)))


class NotString(StepError):  # pragma: no cover

    def __init__(self, name, actual):
        msg = '%s: value must be string, got %r' % (name, actual)
        super().__init__(msg)


class IsEmptyString(StepError):  # pragma: no cover

    def __init__(self, name, actual):
        msg = '%s: value must not be an empty string, got %r' % (name, actual)
        super().__init__(msg)
