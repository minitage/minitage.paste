# Copyright (C) 2009, Mathieu PASQUET <kiorky@cryptelium.net>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 3. Neither the name of the <ORGANIZATION> nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.



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
