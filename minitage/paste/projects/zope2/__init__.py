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
from minitage.paste.projects import common
from minitage.paste.common import var
from minitage.core.common  import which
import getpass
import subprocess

class Template(common.Template):

    summary = 'Template for creating a zope2.10.7 project'
    python = 'python-2.4'

    def pre(self, command, output_dir, vars):
        """register catogory, and roll in common,"""
        vars['category'] = 'zope'
        common.Template.pre(self, command, output_dir, vars)
        vars['mode'] = vars['mode'].lower().strip()
        if not vars['inside_minitage']:
            interpreter = None
            try:
                interpreter = which(vars['python'].strip())
            except:
                interpreter = which('python2.4')
            if not interpreter:
                raise Exception('Python interpreter not found')

            # which python version are we using ?
            executable_version = os.popen(
                '%s -c "%s"' % (
                    interpreter,
                    'import sys;print sys.version[:3]'
                )
            ).read().replace('\n', '')
            if executable_version != '2.4':
                print 'Try to find a python 2.4 installation, you didnt give a 2.4 python to paster'
                interpreter = which('python2.4')
                executable_version = os.popen(
                    '%s -c "%s"' % (
                        interpreter,
                        'import sys;print sys.version[:3]'
                    )
                ).read().replace('\n', '')
                if executable_version != '2.4':
                    raise Exception('Incomptable python '
                                    'version: (%s, %s)' % (interpreter,
                                                          executable_version)
                                   )
            executable_prefix = os.path.abspath(
                subprocess.Popen(
                    [interpreter, '-c', 'import sys;print sys.prefix'],
                    stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                    close_fds=True).stdout.read().replace('\n', '')
            )
            vars['xml2'] = os.path.join(executable_prefix, 'lib', 'python2.4', 'site-packages')
            vars['xslt'] = os.path.join(executable_prefix, 'lib', 'python2.4', 'site-packages')
            vars['python'] = interpreter
        if not vars['mode'] in ['zodb', 'relstorage', 'zeo']:
            raise Exception('Invalid mode (not in zeo, zodb, relstorage')

running_user = getpass.getuser()
Template.vars = common.Template.vars \
        + [var('address',
               'Address to listen on',
               default = 'localhost',),
           var('port',
               'Port to listen to',
               default = '8080',),
           var('mode',
               'Mode to use : zodb|relstorage|zeo',
               default = 'zeo'
              ),
           var('zeoaddress',
               'Address for the zeoserver (zeo mode only)',
               default = 'localhost:8100',),
           var('loglevel',
               'log level (DEBUG|INFO|WARNING|ERROR)',
               default = 'INFO',),
           var('debug',
               'Debug mode (on|off)',
               default = 'on',),
           var('login',
               'Administrator login',
               default = 'admin',),
           var('password',
               'Admin Password in the ZMI',
               default = 'admin',),
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
           var('psycopg2',
               'Postgresql python bindings support (y or n)',
               default = 'n',),
           var('mysqldb',
               'Python Mysql bindings support (y or n)',
               default = 'n',),
           var('plone_products',
               'space separeted list of adtionnal products to install: '
               'eg: file://a.tz file://b.tgz',
               default = '',),
           var('plone_eggs',
               'space separeted list of additionnal eggs to install',
               default = '',),
           var('plone_np',
               'space separeted list of nested packages for products '
               'distro part',
               default = '',),
           var('plone_vsp',
               'space separeted list of versionned suffix packages '
               'for product distro part',
               default = '',),
           var('with_wsgi_support',
               'WSGI capabilities (y|n))',
               default = 'y',),
           ]

# vim:set et sts=4 ts=4 tw=80:
