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

from paste.script import templates

from minitage.core import common
from minitage.core import core

__HEADER__ = """\
%(comment)s!/usr/bin/env bash
%(comment)s
%(comment)s Copyright (C) 2008, Mathieu PASQUET <kiorky@cryptelium.net>
%(comment)s This program is free software; you can redistribute it and/or modify
%(comment)s it under the terms of the GNU General Public License as published by
%(comment)s the Free Software Foundation; either version 2 of the License, or
%(comment)s (at your option) any later version.
%(comment)s This program is distributed in the hope that it will be useful,
%(comment)s but WITHOUT ANY WARRANTY; without even the implied warranty of
%(comment)s MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
%(comment)s GNU General Public License for more details. """

class Template(templates.Template):

    summary = 'OVERRIDE ME'
    _template_dir = 'template'
    use_cheetah = True
    read_vars_from_templates = True

    vars = [
        templates.var('project_dependencies',
                      'Dependencies (separated by comma)'),
        templates.var('project_eggs',
                      'Python packages non-eggified like libxml2 '
                      'to be added to the python path '
                      '(separated by comma)'),
    ]

    def __init__(self, name):
        templates.Template.__init__(self, name)
        self.output_dir = os.path.abspath('.')

    def run(self, command, output_dir, vars):
        self.pre(command, output_dir, vars)
        # may we have register variables ?
        if self.output_dir:
            if not os.path.exists(self.output_dir):
                os.makedirs(self.output_dir)
            output_dir = self.output_dir
        if not os.path.isdir(output_dir):
            raise Exception('%s is not a directory' % output_dir)
        self.write_files(command, self.output_dir, vars)
        self.post(command, output_dir, vars)

    def check_vars(self, vars, cmd):
        """add mandatory check"""
        cvars = templates.Template.check_vars(self, vars, cmd)
        for var in cvars:
            for mvar in self.vars:
                if mvar.name == var:
                    if getattr(mvar, 'mandatory', False)\
                       and not cvars[var]:
                        raise Exception('%s must be set' % var)

        return cvars
    
    def read_vars(self, command=None):
        print '\n\n\tWarning: All minitage templates come by default'\
                ' with their dependencies. You ll not have to '\
                'specify them.\n\n'

        return templates.Template.read_vars(self, command)

class var(templates.var):
    """patch pastescript to have mandatory fields"""

    def __init__(self, name, description,
                 default='', should_echo=True,
                mandatory = False):
        templates.var.__init__(self, name, description,
                                default, should_echo)
        self.mandatory = mandatory

# vim:set et sts=4 ts=4 tw=80:
