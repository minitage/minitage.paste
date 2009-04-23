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

# this is largely ispired to Pylons paster template
# idea is to generate a buildout which make comes pylons and paster
# then we use a buildout command recipe to generate the pylons project
# This one will come as an egg in the src/ directory installed by buildout in
# develop mode

import getpass
import pwd
import grp

from minitage.paste.projects import common
from minitage.paste.common import var

running_user = getpass.getuser()
gid = pwd.getpwnam(running_user)[3]
group = grp.getgrgid(gid)[0]

class Template(common.Template):

    summary = 'Template for creating a '\
            'basic pylons project inside minitage'

    def pre(self, command, output_dir, vars):
        """register catogory, and roll in common,"""
        vars['category'] = 'pylons'
        common.Template.pre(self, command, output_dir, vars)

Template.vars = common.Template.vars \
        + [var('version',
               'Version',
               default = '0.0.1',),
           var('author',
               'Author',
               default = running_user,),
           var('author_email',
               'Email',
               default = '%s@%s' % (running_user, 'localhost')),
           var('description',
               'Description',
               default = 'project using pylons (description)'),
            var('psycopg2',
               'Postgresql python bindings support (y or n)',
               default = 'n',),
            var('mysqldb',
                'Python Mysql bindings support (y or n)',
                default = 'n',),
          ]
# vim:set et sts=4 ts=4 tw=80:
