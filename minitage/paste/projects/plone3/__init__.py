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
from ConfigParser import ConfigParser
import shutil
import getpass
import subprocess
import urllib2

import pkg_resources

from paste.script.command import run

from minitage.paste.projects import common
from minitage.paste.common import var
from minitage.core.common  import which, search_latest


easy_shop_eggs = ['easyshop.core',
                  'easyshop.carts',
                  'easyshop.catalog',
                  'easyshop.checkout',
                  'easyshop.criteria',
                  'easyshop.customers',
                  'easyshop.discounts',
                  'easyshop.groups',
                  'easyshop.information',
                  'easyshop.kss',
                  'easyshop.login',
                  'easyshop.management',
                  'easyshop.order',
                  'easyshop.payment',
                  'easyshop.shipping',
                  'easyshop.shop',
                  'easyshop.stocks',
                  'easyshop.taxes',
                 ]
packaged_version = '3.2.1'
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
            if 'mysql' in vars['dbtype']:
                vars['plone_eggs'] += ' psycopg2'
            if 'postgresql' in vars['dbtype']:
                vars['plone_eggs'] += ' psycopg2'
            if 'oracle' in vars['dbtype']:
                vars['plone_eggs'] += ' cx_Oracle'
        vars['plone_eggs'] += ' ZODB3'
        eggs_mappings = {
            'with_wsgi_support': ['repoze.zope2', 'Spawning', 'Deliverance',
                             'ZODB3', 'Paste', 'PasteScript', 'PasteDeploy',],
            'with_psycopg2': ['psycopg2'],
            'with_mysqldb': ['MySQL_python'],
            'with_fss': ['iw.fss'],
            'with_pil': ['PILwoTK'],
            'with_pa': ['Products.PloneArticle'],
            #'with_pboard': ['Products.SimpleAttachment'],
            'with_sgdcg': ['collective.dancing'],
            'with_truegall': ['collective.plonetruegallery'],
            'with_lingua': ['Products.LinguaPlone'],
            'with_cachesetup': ['Products.CacheSetup'],
            'with_easyshop': easy_shop_eggs + ['zc.authorizedotnet'],
            'with_ldap': ['python-ldap',
                          'Products.LDAPUserFolder',
                          'Products.LDAPMultiPlugins',
                          'Products.PloneLDAP',]
        }
        zcml_mappings = {
            'with_easyshop': easy_shop_eggs,
        }
        for var in [k for k in eggs_mappings if vars[k]]:
            for egg in eggs_mappings[var]:
                if not egg in vars['plone_eggs']:
                    vars['plone_eggs'] += ' %s' % egg
        for var in [k for k in zcml_mappings if vars[k]]:
            for egg in zcml_mappings[var]:
                if not egg in vars['plone_zcml']:
                    vars['plone_zcml'] += ' %s' % egg
        versions = []
        vars['plone_versions'] = versions
        if vars['with_pa']:
            vars['plone_versions'].append(('Products.PloneArticle', '4.1.2',))
        if not vars['mode'] in ['zodb', 'relstorage', 'zeo']:
            raise Exception('Invalid mode (not in zeo, zodb, relstorage')
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        cwd = os.getcwd()
        pargs = ['create', '-t', 'plone3_buildout', vars['project'],
                 'zope2_install=""', 'debug_mode=off', 'verbose_security=off',
                 'plone_products_install=""', '--no-interactive']
        for var in vars:
            pargs.append('%s=%s' % (var, vars[var]))
        if not os.path.exists(self.output_dir):
            self.makedirs(self.output_dir)
        vars['plone_products_install'] = ''
        vars['zope2_install'] = ''
        vars['debug_mode'] = 'off'
        vars['verbose_security'] = 'off'
        # running plone 3 buildout and getting stuff from it.
        try:
            ep = pkg_resources.load_entry_point(
                'ZopeSkel', 'paste.paster_create_template', 'plone3_buildout'
            )
            p3 = ep(self)
            p3.check_vars(vars, command)
            p3.run(command, vars['path'], vars)
            try:
                etc = os.path.join(vars['path'], 'etc')
                if not os.path.isdir(etc):
                    os.makedirs(etc)
                cfg = os.path.join(vars['path'], 'buildout.cfg')
                dst = os.path.join(vars['path'],
                                   'etc', 'plone3.buildout.cfg')
                vdst = os.path.join(vars['path'],
                                   'etc', 'plone3.versions.cfg')
                open(vdst, 'w').write('')
                p = ConfigParser()
                p.read(dst)
                ext = p._sections.get('buildout', {}).get('extends', '')
                if ext:
                    if ext.startswith('http') and ext.endswith('cfg'):
                        try:
                            open(vdst, 'w').write(
                                urllib2.urlopen(ext).read()
                            )
                        except Exception, e:
                            shutil.copy2(
                                pkg_resources.resource_filename(
                                    'minitage.paste',
                                    'projects/plone3/versions.cfg'
                                ),
                                vdst
                            )
                            self.lastlogs.append(
                                "Versions have not been fixed, be ware. Are"
                                " you connected to the internet (%s).\n" % e
                            )
                            self.lastlogs.append(
                                "%s" % (
                                    'As a default, we will take an already'
                                    ' downloaded versions.cfg matching plone'
                                    ' %s.\n' %
                                    packaged_version
                                )
                            )
                os.rename(cfg, dst)
            except Exception, e:
                print
                print
                print "%s" % ("Plone folks have changed their paster, we didnt get any"
                               " buildout, %s" %e)
                print
                print
        except Exception, e:
            print 'Error executing plone3 buildout, %s'%e

running_user = getpass.getuser()
Template.vars = common.Template.vars \
        + [var('address',
               'Address to listen on',
               default = 'localhost',),
           var('http_port',
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
           var('zope_user',
               'Administrator login',
               default = 'admin',),
           var('zope_password',
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
           var('with_pil',
               'Python imaging support (dangerous to disable) (y/n)',
               default = 'y',),
           var('with_fss',
               'File System Storage support, see http://plone.org/products/filesystemstorage: y/n',
               default = 'y',),
           var('with_cpwkf', 'CMFPlacefulWorkflow, see http://plone.org/products/cmfplacefulworkflow/: y/n',
               default='n'),
           var('with_pa', 'Plone Article, see http://plone.org/products/plonearticle/: y/n',
               default='n'),
           var('with_easyshop', 'Easy Shop, see http://www.geteasyshop.com: y/n',
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
