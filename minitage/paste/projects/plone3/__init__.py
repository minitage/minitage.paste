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
import shutil
import getpass
import re
import subprocess
import urllib2

import pkg_resources

from paste.script.command import run
from iniparse import ConfigParser

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

eggs_mappings = {
    'with_binding_ldap': ['python-ldap'],
    'with_ploneproduct_ldap': ['python-ldap', 'Products.LDAPUserFolder', 'Products.LDAPMultiPlugins', 'Products.PloneLDAP',],
    'with_database_mysql': ['MySQL_python'],
    'with_database_oracle': ['cx_Oracle'],
    'with_database_postgresql': ['psycopg2'],
    'with_tool_ipython': ['ipython'],
    'with_binding_pil': ['PILwoTK'],
    'with_ploneproduct_cachesetup': ['Products.CacheSetup'],
    'with_ploneproduct_easyshop': easy_shop_eggs + ['zc.authorizedotnet'],
    'with_ploneproduct_fss': ['iw.fss', 'atreal.patchfss'],
    'with_ploneproduct_lingua': ['Products.LinguaPlone'],
    'with_ploneproduct_p4a_cal': ['p4a.plonecalendar', 'p4a.ploneevent',],
    'with_ploneproduct_p4a_vid': ['p4a.common', 'p4a.z2utils', 'p4a.fileimage', 'p4a.video', 'p4a.plonevideo', 'p4a.plonevideoembed',],
    'with_ploneproduct_plonearticle': ['Products.PloneArticle'],
    'with_ploneproduct_ploneboard': ['Products.Ploneboard', 'Products.SimpleAttachment'],
    'with_ploneproduct_plonesurvey': ['Products.PloneSurvey '],
    'with_ploneproduct_quillsenabled': ['Products.QuillsEnabled', 'quills.remoteblogging'],
    'with_ploneproduct_quills': ['Products.Quills', 'quills.remoteblogging'],
    'with_ploneproduct_sgdcg': ['collective.dancing'],
    'with_ploneproduct_truegallery': ['collective.plonetruegallery', 'gdata', 'flickrapi'],
    'with_ploneproduct_wc_dd_menu': ['webcouturier.dropdownmenu'],
    'with_ploneproduct_ploneboard': ['Products.Ploneboard',],
    'with_ploneproduct_collage': ['Products.Collage',],
    'with_ploneproduct_flowplayer': ['collective.flowplayer',],
    'with_ploneproduct_ploneformgen': ['Products.PloneFormGen',],
    'with_tool_zopeskel': ['ZopeSkel',],
    'with_ploneproduct_tal_portlet': ['collective.portlet.tal',],
    'with_ploneproduct_contentlicensing': ['collective.contentlicensing',],
    'with_ploneproduct_csvreplica': ['Products.csvreplicata',],
    'with_ploneproduct_schematuning': ['archetypes.schematuning',],
    'with_ploneproduct_atbackref': ['Products.ATBackRef'],
    'with_wsgi_support': ['repoze.zope2', 'Spawning', 'Deliverance', 'ZODB3', 'Paste', 'PasteScript', 'PasteDeploy',],
}
zcml_mappings = {
    'with_ploneproduct_contentlicensing': ['collective.contentlicensing',],
    'with_ploneproduct_easyshop': easy_shop_eggs,
    'with_ploneproduct_flowplayer': ['collective.flowplayer',],
    #http://pypi.python.org/pypi/atreal.patchfss/1.0.0
    'with_ploneproduct_fss': ['iw.fss-meta', 'atreal.patchfss'],#'iw.fss',
    'with_ploneproduct_p4a_cal': ['p4a.plonecalendar', 'p4a.plonecalendar-meta', 'p4a.ploneevent',],
    'with_ploneproduct_p4a_vid': [ 'p4a.plonevideo', 'p4a.plonevideoembed', 'p4a.fileimage',],
    'with_ploneproduct_quillsenabled': ['Products.QuillsEnabled', 'quills.remoteblogging'],
    'with_ploneproduct_quills': ['Products.Quills'],
    'with_ploneproduct_sgdcg': ['collective.dancing'],
    'with_ploneproduct_tal_portlet': ['collective.portlet.tal',],
    'with_ploneproduct_truegallery': ['collective.plonetruegallery',],
    'with_ploneproduct_wc_dd_menu': ['webcouturier.dropdownmenu'],
}

versions_mappings = {
    'RelStorage': [('ZODB3', '3.7.2')]
}
p4a = [('p4a.subtyper', '1.1.0'),
       ('p4a.z2utils', '1.0.2'),
       ('p4a.common', '1.0.3'),
      ]
checked_versions_mappings = {
    'with_ploneproduct_plonearticle': [('Products.PloneArticle', '4.1.4',)],
    'with_ploneproduct_p4a_vid': [('hachoir-parser', '1.2.1'),
                                  ('hachoir-metadata', '1.2.1'),
                                  ('hachoir-core', '1.2.1'),
                                  ('p4a.fileimage', '1.0.2'),
                                  ('p4a.video', '1.1.1'),
                                  ('p4a.plonevideo', '1.1.1'),
                                  ('p4a.plonevideoembed', '1.1'),
                                 ]+p4a,
    'with_ploneproduct_p4a_cal' : [('p4a.plonecalendar',  '2.0a2'),
                                   ('p4a.calendar',  '2.0a1'),
                                   ('python_dateutil',  '1.4.1'),
                                   ('p4a.ploneevent',  '0.5'),
                                   ('dateable.chronos',  '0.4'),
                                   ('dateable.kalends',  '0.4'),
                                  ]+p4a,

    'with_ploneproduct_lingua': [('Products.LinguaPlone', '3.0a3'),
                                 ('Products.PloneLanguageTool', '3.0.2'),
                                ],
    'with_ploneproduct_ldap': [('Products.LDAPUserFolder', '2.12'),
                               ('Products.LDAPMultiPlugins', '1.7'),
                               ('Products.PloneLDAP', '1.1'),
                              ],
    'with_ploneproduct_fss': [('iw.fss', '2.7.6'),
                              ('iw.recipe.fss', '0.2.1'),
                             ],
    'with_ploneproduct_ploneboard': [('Products.SimpleAttachment', '3.0.2')],
    'with_ploneproduct_truegallery': [('collective.plonetruegallery', '0.7rc1')],
}

packaged_version = '3.3.1'
class Template(common.Template):

    summary = 'Template for creating a plone3 project'
    python = 'python-2.4'

    def read_vars(self, command=None):
        print '%s' % (
            '---------------------------------------------------------\n'
            '\tPlone 3 needs a python 2.4 to run:\n'
            '\t * if you do not fill anything, it will use minitage or system\'s one\n'
            '\t * if you do not provide one explicitly, it will use minitage or system\'s one\n'
            '\t * Bindings will be automaticly included when you choose for example relstorage/mysql or plone ldap support.\n'
            '\tAditionnaly you ll got two buildouts for production (buildout.cfg) and develoment mode (dev.cfg).\n'
            '\tYou can also activate or safely ignore questions about zeoserver and relstorage if you do not use them.\n'
            '---------------------------------------------------------\n'
        )
        vars = common.Template.read_vars(self, command)
        for i, var in enumerate(vars[:]):
            if var.name in ['relstorage_dbname', 'relstorage_dbuser'] and command:
                vars[i].default = command.args[0]
        return vars

    def pre(self, command, output_dir, vars):
        """register catogory, and roll in common,"""
        vars['category'] = 'zope'
        vars['includesdirs'] = ''
        common.Template.pre(self, command, output_dir, vars)
        vars['mode'] = vars['mode'].lower().strip()

        # transforming eggs requirements as lists
        vars['additional_eggs'] = [a.strip() for a in vars['additional_eggs'].split(',')]
        vars['plone_zcml'] = [a.strip() for a in vars['plone_zcml'].split(',')]

        # plone system dependencies
        if vars['inside_minitage']:
            for i in ['libxml2', 'libxslt', 'pilwotk', 'libiconv']:
                vars['opt_deps'] += ' %s' %  search_latest('%s.*' % i, vars['minilays'])

        # databases
        minitage_dbs = ['mysql', 'postgresql']
        for db in minitage_dbs:
            if vars['with_database_%s' % db]:
                vars['opt_deps'] += ' %s' % search_latest('%s-\d\.\d*'% db, vars['minilays'])

        # openldap
        if vars['with_binding_ldap'] and vars['inside_minitage']:
            cs = search_latest('cyrus-sasl-\d\.\d*', vars['minilays'])
            vars['opt_deps'] += ' %s %s' % (
                search_latest('openldap-\d\.\d*', vars['minilays']),
                cs
            )
            vars['includesdirs'] = '\n    %s'%  os.path.join(
                vars['mt'], cs, 'parts', 'part', 'include', 'sasl'
            )

        # relstorage
        if 'relstorage' in vars['mode']:
            vars['additional_eggs'].append('#Relstorage')
            vars['additional_eggs'].append('Relstorage')
            for db in [var.replace('with_database_', '')
                        for var in vars
                        if 'with_database_' in var]:
                if db in vars['relstorage_type']:
                    vars['additional_eggs'].extend(
                        [a
                         for a in eggs_mappings['with_database_%s'%db]
                         if not a in vars['additional_eggs']
                        ]
                    )
                    if db in minitage_dbs and vars['inside_minitage']:
                        vars['opt_deps'] += ' %s' % search_latest('%s-\d\.\d*'% db, vars['minilays'])

        # ZODB3 from egg
        vars['additional_eggs'].append('#ZODB3 is installed as an EGG!')
        vars['additional_eggs'].append('ZODB3')

        # plone eggs selections
        for var in [k for k in eggs_mappings if vars[k]]:
            vars['additional_eggs'].append('#%s'%var)
            for egg in eggs_mappings[var]:
                if not '%s\n' % egg in vars['additional_eggs']:
                    if not egg in vars['additional_eggs']:
                        vars['additional_eggs'].append(egg)

        # associated zcml slugs
        for var in [k for k in zcml_mappings if vars[k]]:
            vars['plone_zcml'].append('#%s'%var)
            for egg in zcml_mappings[var]:
                if not '%s\n' % egg in vars['plone_zcml']:
                    if not egg in vars['plone_zcml']:
                        vars['plone_zcml'].append(egg)

        # do we need some pinned version
        vars['plone_versions'] = []
        for var in versions_mappings:
            vars['plone_versions'].append(('# %s' % var, '',))
            for pin in versions_mappings[var]:
                vars['plone_versions'].append(pin)

        if vars["with_checked_versions"]:
            for var in checked_versions_mappings:
                if vars[var]:
                    vars['plone_versions'].append(('# %s' % var, '',))
                    for pin in checked_versions_mappings[var]:
                        vars['plone_versions'].append(pin)

        if not vars['mode'] in ['zodb', 'relstorage', 'zeo']:
            raise Exception('Invalid mode (not in zeo, zodb, relstorage')
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        if vars['with_ploneproduct_maps']:
            vars['plone_products'] += ' %s' % 'http://plone.org/products/maps/releases/1.1/maps-1-1.tgz'

        cwd = os.getcwd()
        if not os.path.exists(self.output_dir):
            self.makedirs(self.output_dir)
        # install also the official template from ZopeSkel, setting its variables
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
            coo = command.options.overwrite
            command.options.overwrite = True
            p3.check_vars(vars, command)
            p3.run(command, vars['path'], vars)
            command.options.overwrite = coo
            try:
                etc = os.path.join(vars['path'], 'etc')
                if not os.path.isdir(etc):
                    os.makedirs(etc)
                cfg = os.path.join(vars['path'], 'buildout.cfg')
                dst = os.path.join(vars['path'],
                                   'etc', 'plone3.buildout.cfg')
                vdst = os.path.join(vars['path'],
                                   'etc', 'plone3.versions.cfg')
                bc = ConfigParser()
                bc.read(cfg)
                ext = ''
                try:
                    ext = bc.get('buildout', 'extends')
                except:
                    pass
                if ext:
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
                # remove the extends bits in the plone3 buildout
                if not bc.has_section('buildout'):
                    bc.add_section('buildout')

                bc.set(
                    'buildout',
                    'extends',
                    'plone3.versions.cfg'
                )
                bc.write(open(dst, 'w'))
            except Exception, e:
                print
                print
                print "%s" % ("Plone folks have changed their paster, we didnt get any"
                               " buildout, %s" %e)
                print
                print
        except Exception, e:
            print 'Error executing plone3 buildout, %s'%e

        # be sure our special python is in priority
        vars['opt_deps'] = re.sub('\s*%s\s*' % self.python, ' ', vars['opt_deps'])
        vars['opt_deps'] += " %s" % self.python

running_user = getpass.getuser()
sd_str = '%s' % (
    'Singing & Dancing NewsLetter, see http://plone.org/products/dancing'
    ' S&D is known to lead to multiple buildout installation errors.'
    ' Be sure to activate it and debug the errors. y/n'
)
Template.vars = common.Template.vars \
        + [var('plone_version', 'Plone version, default is the one supported and packaged', default = '3.3.1',),
           var('address', 'Address to listen on', default = 'localhost',),
           var('http_port', 'Port to listen to', default = '8080',),
           var('mode', 'Mode to use : zodb|relstorage|zeo', default = 'zodb'),
           var('zeo_address', 'Address for the zeoserver (zeo mode only)', default = 'localhost:8100',),
           var('zope_user', 'Administrator login', default = 'admin',),
           var('zope_password', 'Admin Password in the ZMI', default = 'secret',),
           var('relstorage_type', 'Relstorage database type (only useful for relstorage mode)', default = 'postgresql',),
           var('relstorage_host', 'Relstorage database host (only useful for relstorage mode)', default = 'localhost',),
           var('relstorage_port', 'Relstorage databse port (only useful for relstorage mode). (postgresql : 5432, mysql : 3306)', default = '5432',),
           var('relstorage_dbname', 'Relstorage databse name (only useful for relstorage mode)', default = 'minitagedb',),
           var('relstorage_dbuser', 'Relstorage user (only useful for relstorage mode)', default = running_user),
           var('relstorage_password', 'Relstorage password (only useful for relstorage mode)', default = 'secret',),
           #http://pypi.python.org/pypi/atreal.patchfss/1.0.0
           var('with_ploneproduct_fss', 'File System Storage support, see http://plone.org/products/filesystemstorage y/n', default = 'y',),
           var('fss_strategy', 'File System Storage strategy, see http://pypi.python.org/pypi/iw.fss/#storage-strategies (directory, flat, site1, site2)', default = 'directory',),
           var('plone_products', 'space separeted list of adtionnal products to install: eg: file://a.tz file://b.tgz', default = '',),
           var('additional_eggs', 'comma separeted list of additionnal eggs to install', default = '',),
           var('plone_zcml', 'comma separeted list of eggs to include for searching ZCML slugs', default = '',),
           var('plone_np', 'space separeted list of nested packages for products distro part', default = '',),
           var('plone_vsp', 'space separeted list of versionned suffix packages for product distro part', default = '',),
           var('with_binding_ldap', 'LDAP bindings support y/n', default = 'n',),
           var('with_database_mysql', 'Mysql python bindings support y/n', default = 'n',),
           var('with_database_oracle', 'Oracle python bindings support y/n', default = 'n',),
           var('with_database_postgresql', 'Postgresql python bindings support y/n', default = 'n',),
           var('with_binding_pil', 'Python imaging support (dangerous to disable) y/n', default = 'y',),
           var('with_tool_ipython', 'ipython support http://ipython.scipy.org/ y/n', default = 'y',),
           var('with_tool_zopeskel', 'ZopeSkel http://pypi.python.org/pypi/ZopeSkel', default = 'y',),
           var('with_wsgi_support', 'WSGI capabilities y/n', default = 'y',),
           var('plomino_revision', 'Plomino Revision to checkout, see http://plone.org/products/plomino/ y/n', default='HEAD'),
           var('with_checked_versions', 'Use product validated versions that interact well together (can be outdated, please check [versions] in buildout.', default = 'n',),
           var('with_ploneproduct_atbackref', 'ATBAckRef, see http://pypi.python.org/pypi/Products.ATBackRef y/n', default='n'),
           var('with_ploneproduct_cachesetup', 'Cachefu caching Support, see http://plone.org/products/cachefu/ y/n', default='y'),
           var('with_ploneproduct_collage', 'Collage, see http://pypi.python.org/pypi/Products.Collage/ y/n', default='n'),
           var('with_ploneproduct_contentlicensing', 'Content Licensing, see http://pypi.python.org/pypi/collective.contentlicensing y/n', default='n'),
           var('with_ploneproduct_cpwkf', 'CMFPlacefulWorkflow, see http://plone.org/products/cmfplacefulworkflow/ y/n', default='n'),
           var('with_ploneproduct_csvreplica', 'CSV Replicata, see http://pypi.python.org/pypi/Products.csvreplicata (makina users, do not untick) y/n', default='y'),
           var('with_ploneproduct_easyshop', 'Easy Shop, see http://www.geteasyshop.com y/n', default='n'),
           var('with_ploneproduct_flowplayer', 'FlowPlayer, see http://plone.org/products/collective-flowplayer/ y/n', default='n'),
           var('with_ploneproduct_ldap', 'Plone LDAP support, see http://plone.org/products/ploneldap/ y/n', default='n'),
           var('with_ploneproduct_lingua', 'LinguaPlone support, see http://plone.org/products/linguaplone y/n', default='n'),
           var('with_ploneproduct_maps', 'Maps, see http://plone.org/products/maps/ y/n',default='n'),
           var('with_ploneproduct_p4a_cal', 'p4a Calendar, see http://pypi.python.org/pypi/p4a.calendar y/n', default='n'),
           var('with_ploneproduct_p4a_vid', 'p4a Video, see http://www.plone4artists.org/products/plone4artistsvideo y/n', default='n'),
           var('with_ploneproduct_plomino', 'Plomino, see http://plone.org/products/plomino/ y/n', default='n'),
           var('with_ploneproduct_plonearticle', 'Plone Article, see http://plone.org/products/plonearticle/ y/n', default='n'),
           var('with_ploneproduct_ploneboard', 'Plone Board, see http://plone.org/products/ploneboard/ y/n', default='n'),
           var('with_ploneproduct_ploneformgen', 'PloneFormGen, see http://plone.org/products/ploneformgen y/n', default='n'),
           var('with_ploneproduct_plonesurvey', 'PloneSurvey, see http://plone.org/products/plone-survey/releases/1.3.0 y/n', default='n'),
           var('with_ploneproduct_quillsenabled', 'Quills Enabled, see http://pypi.python.org/pypi/Products.QuillsEnabled/ y/n', default='n'),
           var('with_ploneproduct_quills', 'Quills, see http://pypi.python.org/pypi/Products.Quills/ y/n', default='n'),
           var('with_ploneproduct_schematuning', 'Schematuning patch, see http://pypi.python.org/pypi/archetypes.schematuning/ y/n', default='n'),
           var('with_ploneproduct_sgdcg', sd_str, default='n'),
           var('with_ploneproduct_tal_portlet', 'Tal Portlet, see http://pypi.python.org/pypi/collective.portlet.tal y/n', default='n'),
           var('with_ploneproduct_truegallery', 'PloneTrueGallery, see http://plone.org/products/plone-true-gallery/ y/n', default='n'),
           var('with_ploneproduct_vaporisation', 'Vaporisation, see http://plone.org/products/vaporisation/ y/n', default='n'),
           var('with_ploneproduct_wc_dd_menu', 'WebCouturier Dropdown Menu, see http://plone.org/products/webcouturier-dropdownmenu y/n', default='n'),
           ]

# vim:set et sts=4 ts=4 tw=0:
