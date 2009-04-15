#!/usr/bin/env python

# Copyright (C) 2008, Mathieu PASQUET <kiorky@cryptelium.net>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

__docformat__ = 'restructuredtext en'


import os
import sys
from minitage.paste.profils import varnish as common
from paste.script import templates

class Template(common.Template):
    """A Varnish2 template"""

    summary = 'Template for creating a varnish2 instance'

Template.vars = common.common_vars + [
    templates.var('backend', 'Backend', default = 'localhost:8080'),
    templates.var(
        'vp',
        'Daemon prefix',
        default = os.path.join(sys.prefix, 'dependencies',
                               'varnish-2.0.3', 'parts', 'part')
    ),
]

# vim:set et sts=4 ts=4 tw=80:
