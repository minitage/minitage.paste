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
            'basic builbot slave inside minitage'

    def pre(self, command, output_dir, vars):
        """register catogory, and roll in common,"""
        vars['category'] = 'misc'
        common.Template.pre(self, command, output_dir, vars)

Template.vars = common.Template.vars \
        + [var('master_host',
               'Buildbot master port',
               default = 'localhost',),
           var('master_port',
               'Master builbot port for the clients to connect to',
               default = '8999',),
           var('master_password',
               'Password',
               default = 'secret',),
          ]
# vim:set et sts=4 ts=4 tw=80:
