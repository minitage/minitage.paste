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
from minitage.core.common  import which, search_latest
import getpass
import subprocess

class Template(common.Template):

    summary = 'Template for creating a plone3 project'
    python = 'python-2.4'

    def pre(self, command, output_dir, vars):
        """register catogory, and roll in common,"""
        vars['category'] = 'zope'
        common.Template.pre(self, command, output_dir, vars)
        vars['mode'] = vars['mode'].lower().strip()
        if vars['with_psycopg2']:
            vars['opt_deps'] += ' %s' % search_latest('postgresql-\d.\d*', vars['minilays'])
        if vars['with_ldap'] and vars['inside_minitage']:
            vars['opt_deps'] += ' %s' % search_latest('openldap-\d\.\d*', vars['minilays'])
        vars['plone_eggs'] += ' ipython'
        if 'relstorage' in vars['mode']:
            vars['plone_eggs'] += ' RelStorage'
        vars['plone_eggs'] += ' ZODB3'
        eggs_mappings = {
            'with_wsgi_support': ['repoze.zope2', 'Spawning', 'Deliverance',
                             'ZODB3', 'Paste', 'PasteScript', 'PasteDeploy',],
            'with_psycopg2': ['psycopg2'],
            'with_mysqldb': ['MySQL_python'],
            'with_fss': ['iw.fss'],
            'with_pa': ['Products.PloneArticle'],
            #'with_pboard': ['Products.SimpleAttachment'],
            'with_sgdcg': ['collective.dancing'],
            'with_truegall': ['collective.plonetruegallery'],
            'with_lingua': ['Products.LinguaPlone'],
            'with_cachesetup': ['Products.CacheSetup'],
            'with_ldap': ['python-ldap',
                          'Products.LDAPUserFolder',
                          'Products.LDAPMultiPlugins',
                          'Products.PloneLDAP',]

        }
        for var in [k for k in eggs_mappings if vars[k]]:
            for egg in eggs_mappings[var]:
                vars['plone_eggs'] += ' %s' % egg

        versions = []
        vars['plone_versions'] = versions
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
               default = 'zodb'
              ),
           var('zeoaddress',
               'Address for the zeoserver (zeo mode only)',
               default = 'localhost:8100',),
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
           var('plone_products',
               'space separeted list of adtionnal products to install: '
               'eg: file://a.tz file://b.tgz',
               default = '',),
           var('plone_eggs',
               'space separeted list of additionnal eggs to install',
               default = '',),
           var('plone_zcml',
               'space separeted list of eggs to include for searching ZCML slugs',
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
               'WSGI capabilities (y/n))',
               default = 'y',),
           var('with_psycopg2',
               'Postgresql python bindings support (y/n)',
               default = 'n',),
           var('with_mysqldb',
               'Python Mysql bindings support (y/n)',
               default = 'n',),
           var('with_ldap',
               'LDAP bindings support (y/n)',
               default = 'n',),
           var('with_fss',
               'File System Storage support, see http://plone.org/products/filesystemstorage: y/n',
               default = 'y',),
           var('with_cpwkf', 'CMFPlacefulWorkflow, see http://plone.org/products/cmfplacefulworkflow/: y/n',
               default='n'),
           var('with_pa', 'Plone Article, see http://plone.org/products/plonearticle/: y/n',
               default='n'),
#           var('with_pboard', 'Plone Board, see  http://plone.org/products/ploneboard/: y/n',
#               default='n'),
           var('with_sgdcg', 'Singing & Dancing NewsLetter see http://plone.org/products/dancing/: y/n',
               default='n'),
           var('with_truegall', 'PloneTrueGallery see http://plone.org/products/plone-true-gallery/: y/n',
               default='n'),
           var('with_lingua', 'LinguaPlone support, see http://plone.org/products/linguaplone: y/n',
               default='n'),
           var('with_cachesetup', 'Cachefu caching Support, see http://plone.org/products/cachefu/: y/n',
               default='y'),
           ]

# vim:set et sts=4 ts=4 tw=80:
