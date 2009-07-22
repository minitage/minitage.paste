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

import os
import sys
import getpass
import pwd
import grp
import subprocess

from minitage.paste.projects import common
from minitage.paste.common import var
from minitage.core.common import which, search_latest


running_user = getpass.getuser()
gid = pwd.getpwnam(running_user)[3]
group = grp.getgrgid(gid)[0]

class Template(common.Template):
    """A Zope3 template"""

    summary = 'Template for creating a basic zope3 project'
    python = 'python-2.6'

    def post(self, command, output_dir, vars):
        common.Template.post(self, command, output_dir, vars)
        p = os.path.join(vars['path'], 'etc', 'zeoserver.sh.in')
        if os.path.exists(p):
            os.chmod(p, 0755)

    def pre(self, command, output_dir, vars):
        """register catogory, and roll in common,"""
        vars['category'] = 'zope'
        common.Template.pre(self, command, output_dir, vars)
        vars['mode'] = vars['mode'].lower().strip()
        if vars['with_mysqldb']:
            vars['opt_deps'] += ' %s' % search_latest('mysql-\d.\d*', vars['minilays']) 
        if vars['with_psycopg2']:
            vars['opt_deps'] += ' %s' % search_latest('postgresql-\d.\d*', vars['minilays'])
        if not vars['mode'] in ['zodb', 'relstorage', 'zeo']:
            raise Exception('Invalid mode (not in zeo, zodb, relstorage')

Template.vars = common.Template.vars \
        + [var('address',
               'Address to listen on',
               default = 'localhost',),
           var('port',
               'Port to listen to',
               default = '8080',),
           var('zeoaddress',
               'Address for the zeoserver (zeo mode only)',
               default = 'localhost:8100',),
           var('mzeoaddress',
               'Address for the zeoserver monitor (zeo mode only)',
               default = 'localhost:8101',),
           var('user',
               'User',
               default = running_user,),
           var('passwd',
               'Password',
               default = 'admin',),
           var('version',
               'Version',
               default = '0.0.1',),
           var('author',
               'Author',
               default = running_user,),
           var('email',
               'Email',
               default = '%s@%s' % (running_user, 'localhost')),
           var('mode',
               'Mode to use: zodb|relstorage|zeo',
               default = 'zodb'),
           var('with_relstorage',
               'RelStorage support (y|n)',
               default = 'y'),
           var('add_eggs',
               'space separeted list of additionnal eggs to install',
               default = '',),
           var('dbtype',
               'Relstorage database type (only useful for relstorage mode)',
               default = 'postgresql',),
           var('dbhost',
               'Relstorage database host (only useful for relstorage mode)',
               default = 'localhost',),
           var('dbport',
               'Relstorage databse port (only useful for relstorage mode)',
               default = '5432',),
           var('dbname',
               'Relstorage databse name (only useful for relstorage mode)',
               default = 'minitagedb',),
           var('dbuser',
               'Relstorage user (only useful for relstorage mode)',
               default = running_user),
           var('dbpassword',
               'Relstorage password (only useful for relstorage mode)',
               default = 'admin',),
           var('with_psycopg2',
               'Postgresql python bindings support (y or n)',
               default = 'n',),
            var('with_mysqldb',
                'Python Mysql bindings support (y or n)',
                default = 'n',),
]
# vim:set et sts=4 ts=4 tw=80:
