#!/usr/bin/env python

# Copyright (C) 2008, Mathieu PASQUET <kiorky@cryptelium.net>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, # but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

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
            if vars['with_psycopg2']:
                vars['opt_deps'] += ' %s' % (
                    search_latest('postgresql-\d.\d', minilays),
                )
            if (not vars['with_psycopg2']) \
               and (not vars['mysqldb']):
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
