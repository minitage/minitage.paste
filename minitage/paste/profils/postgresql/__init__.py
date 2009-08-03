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
import sys
import grp
import re
import subprocess

from minitage.paste.profils import common
from minitage.core.common import remove_path, which
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
        conf = os.path.join(vars['sys'],
                            'var', 'data',
                            'postgresql',
                            vars['db_name'],
                            'postgresql.conf') 
        if not os.path.exists(conf):
            if not os.path.exists(db_path):
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
            # We are searching in the destination if we
            # already have a postgresql installation.
            # If we have, just register as already installed.
            # and do not initdb.
            # If no pgsql is installed, do initdb/createdb but
            # remove files coming out by templates
            # to be out of overwrite errors.
            ret = os.system("""
                      bash -c ". %s/share/minitage/minitage.env;\
                      initdb  -E 'UTF-8';\
                      pg_ctl -w start ;\
                      createdb ;\
                      pg_ctl stop"
                      """ % (vars['sys'])
                     )
            if ret>0:
                print  "\n\n%s" % (
                    'Error while initiliasing the database.\n'
                    'More likely Postgresql binaries were not found in your path. Do you have'
                    ' built postgresql somewhere or launched minimerge to build it'
                    ' after adding postgresql-x.x to your project minibuild?.'
                )
                sys.exit(1) 
            version = os.popen('bash -c ". %s/share/minitage/minitage.env;initdb --version').read()
            if '8.2' in version:
                vars['lc'] = 'redirect_stderr'
            else:
                vars['lc'] = 'logging_collector'
            for f in ('pg_hba.conf',
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
        conf = os.path.join(vars['sys'],
                            'var', 'data',
                            'postgresql',
                            vars['db_name'],
                            'postgresql.conf')
        confa = os.path.join(vars['sys'],
                            'var', 'data',
                            'postgresql',
                            vars['db_name'],
                            'pg_hba.conf')
        confi = os.path.join(vars['sys'],
                            'var', 'data',
                            'postgresql',
                            vars['db_name'],
                            'pg_ident.conf')
        for filep in ('postgresql.conf',
                     'pg_hba.conf', 'pg_ident.conf'):
            dest = os.path.join(vars['sys'],
                                'etc',
                                'postgresql',
                                '%s_%s.%s' % (
                                    vars['project'],vars['db_name'], filep)
                               )
            orig = os.path.join(vars['sys'],
                                'var', 'data',
                                'postgresql',
                                vars['db_name'],
                                filep)
            if not os.path.exists(dest):
                os.symlink(orig, dest)
        confc = open(conf).read()
        if not 'MINITAGE LOGGING' in confc:
            open(conf,'w').write(confc +
                """
# MINITAGE LOGGING
log_directory = '%(sys)s/var/log/postgresql/coursorama'
# directory where log files are written,
# can be absolute or relative to PGDATA
log_filename='postgresql-%(p)sY-%(p)sm-%(p)sd.log'
%(lc)s=true
                                 """ % {
                                     'sys':vars['sys'], 'p':'%', 'lc': vars['lc']
                                 })
        infos = "%s" % (
            "    * You can look for wrappers to various postgresql scripts located in %s. You must use them as they are configured to use some useful defaults to connect to your database.\n"
            "    * A configuration file for your postgresql instance has been linked from %s to %s.\n"
            "    * A pg_hba file for your postgresql instance has been linked from %s to %s.\n"
            "    * A pg_ident file for your postgresql instance has been linked from %s to %s.\n"
            "    * A init script to start your server is available in %s.\n"
            "    * A logrotate configuration file to handle your logs can be linked in global scope, it is available in %s.\n"
            "    *  The datadir is located under %s.\n"
            "    *You can use pypgoptimizator to Tune automaticly your postgresql:\n"
            "      easy_install pypgoptimizator\n"
            "      pypgoptimizator -i %s -o %s\n"
            "" % (
                '"%s'%os.path.join(
                    vars['sys'], 'bin', '%s.*" eg : %s.psql' % (
                        vars['db_name'],
                        vars['db_name']
                    )
                ),
                conf,
                os.path.join(
                    vars['sys'], 'etc', 'postgresql', '%s_%s.%s' % (
                        vars['project'], vars['db_name'], 'postgresql.conf'
                    )
                ),
                confa,
                os.path.join(
                    vars['sys'], 'etc', 'postgresql', '%s_%s.%s' % (
                        vars['project'], vars['db_name'], 'pg_hba.conf'
                    )
                ),
                confi,
                os.path.join(
                    vars['sys'], 'etc', 'postgresql', '%s_%s.%s' % (
                        vars['project'], vars['db_name'], 'pg_ident.conf'
                    )
                ),
                os.path.join(
                    vars['sys'], 'etc', 'init.d', 'postgresql_%s.%s' %(
                        vars['project'], vars['db_name']

                    )
                ),
                os.path.join(
                    vars['sys'], 'etc', 'logrotate.d', '%s_%s.postgresql' %(
                        vars['project'], vars['db_name']
                    )
                ),
                os.path.dirname(conf),
                conf, conf
            )
        )
        README = os.path.join(vars['path'],
                              'README.postgresql.%s-%s' % (
                                  vars['project'],
                                  vars['db_name']
                              )
                             )
        open(README, 'w').write(infos)
        print "Installation is now finished."
        print infos
        print "Those informations have been saved in %s." % README


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
                ]
# vim:set et sts=4 ts=4 tw=80:
