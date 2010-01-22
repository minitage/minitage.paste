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
import tempfile
import time

from minitage.paste.instances import common
from minitage.core.common import remove_path
from paste.script import templates

re_flags = re.M|re.U|re.I|re.S

class Template(common.Template):

    summary = 'Template for creating a postgresql instance'
    _template_dir = 'template'
    use_cheetah = True
    mysql_present = False
    first_run = False


    def pre(self, command, output_dir, vars):
        common.Template.pre(self, command, output_dir, vars)
        db_path = os.path.join(
            vars['sys'], 'var', 'data', 'mysql', vars['db_name']
        )
        if not 'my_version' in vars:
            vars['my_version'] = '5.1'
        if not os.path.isdir(db_path):
            self.first_run = True

    def post(self, command, output_dir, vars):
        db_path = os.path.join(
            vars['sys'], 'var', 'data', 'mysql', vars['db_name']
        )
        if self.first_run:
            os.environ['LANG'] = os.environ['LC_ALL'] = 'C'
            os.environ['MYSQL_HOST'] = vars['db_host']
            os.environ['MYSQL_TCP_PORT'] = vars['db_port']
            os.environ['USER'] = vars['db_user']
            os.environ['MYSQL_HOME'] = os.path.join(vars['sys'], 'var', 'data',
                                                     'mysql', vars['db_name'])
            os.system("""
                      bash -c \". %s/share/minitage/minitage.env;\
                      cd %s;\
                      mysql_install_db --defaults-file=my.cnf --verbose --datadir=%s\
                      \"""" % (vars['sys'], db_path, db_path))
            os.system("""
                      bash -c ". %s/share/minitage/minitage.env;\
                      cd %s;\
                      mysqld_safe --defaults-file=my.cnf&\
                      \"""" % (vars['sys'], db_path))
            time.sleep(2)
            db_infos = {'sys':vars['sys'],
                        'db': db_path,
                        'db_name': vars['db_name'],
                        'db_user': vars['db_user'],
                        'pourcent': '%',
                        'root_password': vars['root_password'],
                        'db_password': vars['password'],
                       }
            os.system("""
                      bash -c ". %(sys)s/share/minitage/minitage.env;\
                      cd %(db)s;\
                      mysqladmin --defaults-file=my.cnf -w30 -u root create %(db_name)s;"\
                      """ % db_infos)
            fp = tempfile.mkstemp()[1]
            open(fp, 'w').write(
"""
use %(db_name)s;

GRANT ALL PRIVILEGES 
ON %(db_name)s 
to '%(db_user)s'@'%(pourcent)s' 
IDENTIFIED BY '%(db_password)s' 
WITH GRANT OPTION;

GRANT ALL PRIVILEGES 
ON %(db_name)s 
to '%(db_user)s'@'localhost' 
IDENTIFIED BY '%(db_password)s' 
WITH GRANT OPTION;
""" % db_infos)
            db_infos['fp'] = fp
            print fp
            os.system("""bash -c ". %(sys)s/share/minitage/minitage.env;\
                      cd %(db)s;\
                      mysql --defaults-file=my.cnf -u root < '%(fp)s'"\
                      """ % db_infos)
            os.remove(fp)
            os.system("""bash -c ". %(sys)s/share/minitage/minitage.env;\
                      cd %(db)s;\
                      mysqladmin --defaults-file=my.cnf -w30 -u root password '%(root_password)s';"\
                      """ % db_infos)
            os.system("""
                      bash -c ". %(sys)s/share/minitage/minitage.env;\
                      cd %(db)s;\
                      mysqladmin --defaults-file=my.cnf -w30 -u root -p%(db_password)s shutdown"\
                      """ % db_infos)
        sys = vars['sys']
        dirs = [os.path.join(sys, 'bin'),
                os.path.join(sys, 'etc', 'init.d')]
        for directory in dirs:
            for filep in os.listdir(directory):
                p = os.path.join(directory, filep)
                os.chmod(p, stat.S_IRGRP|stat.S_IXGRP|stat.S_IRWXU)

        # be nice, link some files
        conf = os.path.join(
            vars['sys'],
            'var',
            'data',
            'mysql',
            vars['db_name'],
            'my.cnf')
        for filep in ('my.cnf',):
            dest = os.path.join(vars['sys'],
                                'etc',
                                'mysql',
                                '%s_%s.%s' % (
                                    vars['project'], vars['db_name'], filep)
                               )
            orig = os.path.join(vars['sys'],
                                'var', 'data',
                                'mysql',
                                vars['db_name'],
                                filep)
            if not os.path.exists(dest):
                os.symlink(orig, dest)
            confc = open(conf).read()

        infos = "%s" % (
            "    * You can look for wrappers to various mysql scripts located in %s. You must use them as they are configured to use some useful defaults to connect to your database.\n"
            "    * A configuration file for your mysql instance has been linked from %s to %s.\n"
            "    * A init script to start your server is available in %s.\n"
            "    * A logrotate configuration file to handle your logs can be linked in global scope, it is available in %s.\n"
            "    * The datadir is located under %s.\n"
            "    * Be aware to use user options like -u and -p to connect to your server.\n"
            "" % (
                '"%s'%os.path.join(
                    vars['sys'], 'bin', '%s.*" eg : %s.mysql' % (
                        vars['db_name'],
                        vars['db_name']
                    )
                ),
                os.path.join(db_path, 'my.cnf'),
                os.path.join(
                    vars['sys'], 'etc', 'mysql', '%s_%s.%s' % (
                        vars['project'], vars['db_name'], 'my.cnf'
                    )
                ),
                os.path.join(
                    vars['sys'], 'etc', 'init.d', '%s_mysql.%s' %(
                        vars['project'], vars['db_name']

                    )
                ),
                os.path.join(
                    vars['sys'], 'etc', 'logrotate.d', '%s_%s.mysql' %(
                        vars['project'], vars['db_name']
                    )
                ),
                db_path,
            )
        )
        README = os.path.join(vars['path'],
                              'README.mysql.%s-%s' % (
                                  vars['project'],
                                  vars['db_name']
                              )
                             )
        open(README, 'w').write(infos)
        print "Installation is now finished."
        print infos
        print "Those informations have been saved in %s." % README

Template.required_templates = ['minitage.instances.env']
running_user = getpass.getuser()
gid = pwd.getpwnam(running_user)[3]
#group = grp.getgrgid(gid)[0]
Template.vars = common.Template.vars + \
                [
                templates.var('mysql_ver', 'Mysql major version (50|51)', default = '51'),
                templates.var('db_name', 'Database name', default = 'minitagedb'),
                templates.var('db_user', 'Default user', default = running_user),
                templates.var('db_host', 'Host to listen on', default = 'localhost'),
                templates.var('db_port', 'Port to listen to', default = '3306'),
                templates.var('root_password', 'Mysql root password', default = 'secret'),
                templates.var('password', 'Database password', default = 'secret'),
                ]
# vim:set et sts=4 ts=4 tw=80:
