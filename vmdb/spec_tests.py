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


import io
import os
import tempfile
import unittest

import yaml

import vmdb


class SpecTests(unittest.TestCase):

    spec_yaml = '''
    steps:
      - step: foo
        arg: "{{ var1 }}"
        number: 0711
      - step: bar
    '''

    def setUp(self):
        self.filename = write_temp_file(bytes(self.spec_yaml, 'ascii'))
        self.spec = vmdb.Spec()

    def tearDown(self):
        if os.path.exists(self.filename):
            os.remove(self.filename)

    def test_loads_spec(self):
        self.spec.load_file(open(self.filename))
        self.assertEqual(self.spec.as_dict(), as_dict(self.spec_yaml))

    def test_expands_templates(self):
        self.spec.load_file(open(self.filename))
        params = {
            'var1': 'value1',
        }
        steps = self.spec.get_steps(params)
        self.assertEqual(
            steps,
            [
                {
                    'step': 'foo',
                    'arg': 'value1',
                    'number': 0o711,
                },
                {
                    'step': 'bar',
                },
            ]
        )

class ExpandTemplatesTests(unittest.TestCase):

    def test_raises_assert_if_given_incomprehensible_value(self):
        with self.assertRaises(AssertionError):
            vmdb.expand_templates(None, {})

    def test_returns_same_given_string_without_template(self):
        self.assertEqual(vmdb.expand_templates('foo', {}), 'foo')

    def test_expands_simple_string_template(self):
        params = {
            'foo': 'bar',
        }
        self.assertEqual(vmdb.expand_templates('{{ foo }}', params), 'bar')

    def test_expands_list_of_templates(self):
        params = {
            'foo': 'bar',
        }
        self.assertEqual(vmdb.expand_templates(['{{ foo }}'], params), ['bar'])

    def test_expands_dict_of_templates(self):
        params = {
            'foo': 'bar',
        }
        self.assertEqual(
            vmdb.expand_templates({'key': '{{ foo }}'}, params),
            {'key': 'bar'}
        )


def write_temp_file(data):
    fd, filename = tempfile.mkstemp()
    os.write(fd, data)
    os.close(fd)
    return filename


def as_dict(yaml_text):
    with io.StringIO(yaml_text) as f:
        return yaml.safe_load(f)
