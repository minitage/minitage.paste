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
from minitage.paste.projects import common
from minitage.paste.common import var
from minitage.core.common  import which, search_latest
import getpass
import subprocess

class Template(common.Template):

    summary = 'Template for creating a plone3 project'
    python = 'python-2.4'

    def read_vars(self, command=None):
        print '%s' % (
            '---------------------------------------------------------\n'
            '\tPlone 3 needs a python 2.4 to run:\n'
            '\t * if you do not fill anything, it will use minitage or system\'s one\n'
            '\t * if you do not provide one explicitly, it will use minitage or' 'system\'s one\n'
            '\tAditionnaly you ll got two buildouts for production (buildout.cfg) and develoment mode (dev.cfg).\n'
            '\tYou can also activate or safely ignore questions about zeoserver and relstorage if you do not use them.\n'
            '---------------------------------------------------------\n'
        )
        return common.Template.read_vars(self, command)

    def pre(self, command, output_dir, vars):
        """register catogory, and roll in common,"""
        vars['category'] = 'zope'
        vars['includesdirs'] = ''
        common.Template.pre(self, command, output_dir, vars)
        vars['mode'] = vars['mode'].lower().strip()
        if vars['inside_minitage']:
            for i in ['libxml2', 'libxslt', 'pilwotk', 'libiconv']:
                vars['opt_deps'] += ' %s' %  search_latest('%s.*' % i, vars['minilays'])
        if vars['with_mysqldb']:
            vars['opt_deps'] += ' %s' % search_latest('mysql-\d.\d*', vars['minilays'])
        if vars['with_psycopg2']:
            vars['opt_deps'] += ' %s' % search_latest('postgresql-\d.\d*', vars['minilays'])
        if vars['with_ldap'] and vars['inside_minitage']:
            vars['opt_deps'] += ' %s' % search_latest('openldap-\d\.\d*', vars['minilays'])
            cs = search_latest('cyrus-sasl-\d\.\d*', vars['minilays'])
            vars['opt_deps'] += ' %s' % cs
            vars['includesdirs'] = '\n    %s'%  os.path.join(
                vars['mt'], cs, 'parts', 'part', 'include', 'sasl'
            )

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
        if vars['with_pa']:
            vars['plone_versions'].append(('Products.PloneArticle', '4.1.2',))
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
           var('with_cachesetup', 'Cachefu caching Support, see http://plone.org/products/cachefu/: y/n',
               default='y'), 
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
               'Relstorage databse port (only useful for relstorage mode).'
               ' (postgresql : 5432, mysql : 3306)',
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
           var('with_sgdcg', 'Singing & Dancing NewsLetter see'
               'http://plone.org/products/dancing/: y/n.'
               'S&D is known to lead to multiple buildout installation errors.'
               'Be sure to activate it and debug the errors.',
               default='n'),
           var('with_truegall', 'PloneTrueGallery see http://plone.org/products/plone-true-gallery/: y/n',
               default='n'),
           var('with_lingua', 'LinguaPlone support, see http://plone.org/products/linguaplone: y/n',
               default='n'),
           ]

# vim:set et sts=4 ts=4 tw=80:
