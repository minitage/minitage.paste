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

import getpass
import pwd
import grp
import os


from minitage.paste.projects import common
from minitage.paste.common import var
from minitage.core.common import  search_latest


running_user = getpass.getuser()
gid = pwd.getpwnam(running_user)[3]
group = grp.getgrgid(gid)[0]

class Template(common.Template):

    summary = 'Template for creating a '\
            'basic django project inside minitage'


    def pre(self, command, output_dir, vars):
        """register catogory, and roll in common,"""
        vars['category'] = 'django'
        common.Template.pre(self, command, output_dir, vars)
        if vars['inside_minitage']:
            minilays = os.path.join(self.output_dir, 'minilays')
            if not 'official' in vars['official']:
                vars['opt_deps'] = search_latest('subversion-\d.\d', minilays)
            if vars['with_mysqldb']:
                vars['opt_deps'] += ' %s' % search_latest('mysql-\d.\d*', vars['minilays'])
            if vars['with_psycopg2']:
                vars['opt_deps'] += ' %s' % (
                    search_latest('postgresql-\d.\d', minilays),
                )
            if (not vars['with_psycopg2']) \
               and (not vars['with_mysqldb']):
                vars['opt_deps'] += ' %s' % (
                    search_latest('sqlite-\d.\d', minilays),
                )
            if vars["with_gis"]:
                deps = ['mapnik-\d.\d*',
                        'libmemcache-\d.\d*',
                        'libxml2-\d.\d*',
                        'libxslt-1.\d*',
                        'pilwotk-1.1.\d.\d*',
                        'zlib-1.\d*',
                        'pgrouting-1.\d*',
                        'cairo-1.\d*',
                        'freetype-2.\d*',
                        'fontconfig-2.\d*',
                        'gdal-\d.\d*',
                        'libpng-1.\d*',
                        'pixman-0.\d*',
                       ]
                for dep in deps:
                    vars['opt_deps'] += ' %s' % search_latest(dep, minilays)


Template.vars = common.Template.vars \
        + [var('djangoversion',
               'Django version',
               default = '1.0.2',),
           var('djangorevision',
               'The revision to check out if you don\'t use the official version',
               default = '9503',),
           var('official',
               'Use official version or something from a repository ?  (scm|official)',
               default = 'official',),
           var('djangourl',
               'URL to checkout from the django code',
               default = 'http://code.djangoproject.com/svn/django/tags/releases/1.0.2',),
           var('djangoscm',
               'How to fetch the django code (static|svn|hg)',
               default = 'svn',),
           var('with_sqlite',
               'SQLite python bindings support (y or n)',
               default = 'y',),
           var('with_psycopg2',
               'Postgresql python bindings support (y or n)',
               default = 'n',),
           var('with_gis',
               'Enable Spatial capabilities (GeoDjango, GIS) (y or n)',
               default = 'n',),
           var('with_mysqldb',
               'Python Mysql bindings support (y or n)',
               default = 'n',),
           var('address',
               'Address to listen on',
               default = 'localhost',),
           var('port',
               'Port to listen to',
              default='8000'),
           var('errorh',
               'Werkzeug or WebError for error '
               'handling in development mode? (werkzeug|weberror)',
              default='weberror'),
          ]





# vim:set et sts=4 ts=4 tw=80:
