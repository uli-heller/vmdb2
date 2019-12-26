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


import jinja2
import yaml


class Spec:

    def __init__(self):
        self._dict = None

    def load_file(self, filename):
        with open(filename) as f:
            self._dict = yaml.safe_load(f)

    def as_dict(self):
        return dict(self._dict)

    def get_steps(self, params):
        return expand_templates(self._dict['steps'], params)


def expand_templates(value, params):
    if isinstance(value, str):
        template = jinja2.Template(value)
        return template.render(**params)
    elif isinstance(value, int):
        return value
    elif isinstance(value, list):
        return [expand_templates(x, params) for x in value]
    elif isinstance(value, dict):
        return {
            key: expand_templates(value[key], params)
            for key in value
        }
    else:
        assert 0, 'Unknown value type: {!r}'.format(value)
