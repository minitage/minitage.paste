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
import stat
import getpass
import pwd
import grp
import re
import subprocess

from minitage.paste.profils import common
from minitage.core.common import remove_path
from paste.script import templates

re_flags = re.M|re.U|re.I|re.S

class Template(common.Template):

    summary = 'Template for creating a postgresql instance'
    _template_dir = 'template'
    use_cheetah = True
    pg_present = False

    def pre(self, command, output_dir, vars):
        common.Template.pre(self, command, output_dir, vars)
        db_path = os.path.join(
            vars['sys'], 'var', 'data', 'postgresql', vars['db_name']
        )
        if not os.path.isdir(db_path):
            os.makedirs(db_path)

            # registering where we initdb
            # which database do we createdb
            os.environ['PGDATA'] = db_path
            os.environ['PGUSER'] = vars['db_user']
            os.environ['PGDATABASE'] = vars['db_name']
            os.environ['PGHOST'] = vars['db_host']
            os.environ['PGPORT'] = vars['db_port']
            # default charsets C avoiding regional problems :)
            os.environ['LANG'] = os.environ['LC_ALL'] = 'C'
            fic = open(
                os.path.join(vars['sys'], 'share', 'minitage', 'minitage.env')
            ).read()
            pgre = re.compile('.*postgresql-([^\s]*)\s.*', re_flags)
            m = pgre.match(fic)
            if m:
                vars['pg_version'] = m.groups()[0]
            vars['log_collector'] = 'logging_collector'
            if vars['pg_version'] == '8.2':
                vars['log_collector'] = 'redirect_stderr'

            # We are searching in the destination if we
            # already have a postgresql installation.
            # If we have, just register as already installed.
            # and do not initdb.
            # If no pgsql is installed, do initdb/createdb but
            # remove files coming out by templates
            # to be out of overwrite errors.
            os.system("""
                      sh -c ". %s/share/minitage/minitage.env;\
                      initdb  -E 'UTF-8';\
                      pg_ctl -w start ;\
                      createdb ;\
                      pg_ctl stop"
                      """ % (vars['sys'])
                     )
            for f in ('postgresql.conf',
                      'pg_hba.conf',
                      'pg_ident.conf' ):
                fp = os.path.join(db_path, f)
                if os.path.isfile(fp):
                    remove_path(fp)

    def post(self, command, output_dir, vars):
        sys = vars['sys']
        dirs = [os.path.join(sys, 'bin'),
                os.path.join(sys, 'etc', 'init.d')]
        for directory in dirs:
            for filep in os.listdir(directory):
                p = os.path.join(directory, filep)
                os.chmod(p, stat.S_IRGRP|stat.S_IXGRP|stat.S_IRWXU)

        # be nice, link some files
        for filep in ('postgresql.conf',
                     'pg_hba.conf', 'pg_ident.conf'):
            dest = os.path.join(vars['sys'],
                                'etc',
                                'postgresql',
                                '%s.%s' % (
                                    vars['db_name'], filep)
                               )
            orig = os.path.join(vars['sys'],
                                'var', 'data',
                                'postgresql',
                                vars['db_name'],
                                filep)
            if not os.path.exists(dest):
                os.symlink(orig, dest)

Template.required_templates = ['minitage.profils.env']
running_user = getpass.getuser()
gid = pwd.getpwnam(running_user)[3]
#group = grp.getgrgid(gid)[0]
Template.vars = common.Template.vars + \
                [
                templates.var('db_name', 'Database name', default = 'minitagedb'),
                templates.var('db_user', 'Default user', default = running_user),
                #templates.var('db_group', 'Default group', default = group),
                templates.var('db_host', 'Host to listen on', default = 'localhost'),
                templates.var('db_port', 'Port to listen to', default = '5432'),
                templates.var('pg_version', 'Version of postgresql to use', default = '8.3'),
                ]
# vim:set et sts=4 ts=4 tw=80:
