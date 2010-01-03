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
from xml.dom.minidom import parse, parseString

import pkg_resources

from paste.script.command import run
from iniparse import ConfigParser

from minitage.paste.projects import common
from minitage.paste.common import var
from minitage.core.common  import which, search_latest

reflags = re.M|re.U|re.S
UNSPACER = re.compile('\s+|\n', reflags)
SPECIALCHARS = re.compile('[.-@_]', reflags)
running_user = getpass.getuser()

default_config = pkg_resources.resource_filename(
    'minitage.paste',
    'projects/plone3/minitage.plone3.xml')
user_config = os.path.join(
    os.path.expanduser('~'),
    '.minitage.plone3.xml'
)

# plone quickinstaller option/names mappings
qi_mappings = {}
# eggs registered as Zope2 packages
z2packages, z2products = {}, {}
# variables discovered via configuration
addons_vars = []
# mappings option/eggs to install
eggs_mappings = {}
# scripts to generate
scripts_mappings = {}
# mappings option/zcml to install
zcml_loading_order = {}
zcml_mappings = {}
# mappings option/versions to pin
versions_mappings = {}
# mappings option/versions to pin if the user wants really stable sets
checked_versions_mappings = {}
# mappings option/productdistros to install
urls_mappings = {}
# mappings option/nested packages/version suffix packages  to install
plone_np_mappings = {}
plone_vsp_mappings = {}

def parse_xmlconfig(xml):
    # discover  additionnal configuration options
    try:
        discovered_options = []
        optsnodes = xml.getElementsByTagName('options')
        if optsnodes:
            for elem in optsnodes:
                opts = elem.getElementsByTagName('option')
                for o in opts:
                    oattrs = dict(o.attributes.items())
                    order = int(oattrs.get('order', 99999))
                    # be sure not to have unicode params there because paster will swallow them up
                    discovered_options.append(
                        (order,
                        var(oattrs.get('name'),
                            UNSPACER.sub(' ', oattrs.get('description', '').strip()),
                            default=oattrs.get('default')
                           )
                        )
                    )
        discovered_options.sort(lambda x, y: x[0] - y[0])
        noecho = [addons_vars.append(o[1]) for o in discovered_options]

        # discover KGS version
        cvs = xml.getElementsByTagName('checkedversions')
        #'with_ploneproduct_plonearticle': [('Products.PloneArticle', '4.1.4',)],
        if cvs:
            for elem in cvs:
                for e in elem.getElementsByTagName('version'):
                    oattrs = dict(e.attributes.items())
                    for option in oattrs['options'].split(','):
                        option = option.strip()
                        if not option in checked_versions_mappings:
                            checked_versions_mappings[option] = []
                        item = (oattrs['p'], oattrs['v'])
                        if not item in checked_versions_mappings[option]:
                            checked_versions_mappings[option].append(item)

        # discover andatory versions pinning
        vs = xml.getElementsByTagName('versions')
        # versions_mappings = {RelStorage': [('ZODB3', '3.7.2')],}
        if vs:
            for elem in vs:
                for e in elem.getElementsByTagName('version'):
                    oattrs = dict(e.attributes.items())
                    for option in oattrs['name'].split(','):
                        option = option.strip()
                        if not option in versions_mappings:
                            versions_mappings[option] = []
                        item = (oattrs['p'], oattrs['v'])
                        if not item in versions_mappings[option]:
                            versions_mappings[option].append(item)

        # quickinstaller mappings discovery
        qi = xml.getElementsByTagName('qi')
        if qi:
            for elem in qi:
                for e in elem.getElementsByTagName('product'):
                    oattrs = dict(e.attributes.items())
                    for option in oattrs['options'].split(','):
                        option = option.strip()
                        if not option in qi_mappings:
                            qi_mappings[option] = []
                        if not oattrs['name'] in qi_mappings:
                            qi_mappings[option].append(oattrs['name'])

        # eggs/zcml discovery
        eggs = xml.getElementsByTagName('eggs')
        if eggs:
            for elem in eggs:
                for e in elem.getElementsByTagName('egg'):
                    oattrs = dict(e.attributes.items())
                    for option in oattrs['options'].split(','):
                        option = option.strip()
                        if not option in eggs_mappings:
                            eggs_mappings[option] = []
                        if not oattrs['name'] in eggs_mappings[option]:
                            eggs_mappings[option].append(oattrs['name'])
                        if 'scripts' in oattrs:
                            if not option in scripts_mappings:
                                scripts_mappings[option] = []
                            for item in oattrs['scripts'].split(','):
                                scripts_mappings[option].append(item)
                        if 'zcml' in oattrs:
                            if not option in zcml_mappings:
                                zcml_mappings[option] = []
                            for slug in oattrs['zcml'].split(','):
                                item = (oattrs['name'], slug.strip())
                                if not item in zcml_mappings[option]:
                                    zcml_mappings[option].append(item)
                                    zcml_loading_order[item] = int(oattrs.get('zcmlorder', '50000'))
                        for d, package in [(z2packages, 'zpackage'), (z2products, 'zproduct')]:
                            if package in oattrs:
                                v = oattrs[package]
                                if not option in d:
                                    d[option] = []
                                if v == 'y':
                                    if not oattrs['name'] in d[option]:
                                        d[option].append(oattrs['name'])
                                else:
                                    #d[option].append('#%s' % oattrs['name'])
                                    zp = [z.strip() for z in oattrs[package].split(',')]
                                    noecho = [d[option].append(z) for z in zp if not z in d[option]]
        # misc product discovery
        miscproducts = xml.getElementsByTagName('miscproducts')
        if miscproducts:
            for elem in miscproducts:
                for e in elem.getElementsByTagName('product'):
                    oattrs = dict(e.attributes.items())
                    for option in oattrs['options'].split(','):
                        option = option.strip()
                        if 'zcml' in oattrs:
                            if not option in zcml_mappings:
                                zcml_mappings[option] = []
                            for slug in oattrs['zcml'].split(','):
                                item = (oattrs['name'], slug.strip())
                                if not item in zcml_mappings[option]:
                                    zcml_mappings[option].append(item)
                                    zcml_loading_order[item] = int(oattrs.get('zcmlorder', '50000'))
                        for d, package in [(z2packages, 'zpackage'), (z2products, 'zproduct')]:
                            if package in oattrs:
                                v = oattrs[package]
                                if not option in d:
                                    d[option] = []
                                if v == 'y':
                                    if not oattrs[package] in d[option]:
                                        d[option].append(oattrs[package])
                                else:
                                    #d[option].append('#%s' % oattrs['name'])
                                    zp = [z.strip() for z in oattrs[package].split(',')]
                                    noecho = [d[option].append(z) for z in zp if not z in d[option]]

        # productdistros handling
        productsdistros = xml.getElementsByTagName('productdistros')
        if productsdistros:
            for elem in productsdistros:
                for e in elem.getElementsByTagName('productdistro'):
                    oattrs = dict(e.attributes.items())
                    for option in oattrs['options'].split(','):
                        option = option.strip()
                        if not option in urls_mappings:
                            urls_mappings[option] = []
                        urls_mappings[option].append(oattrs['url'])
    except Exception, e:
        raise


def init_vars():
    for config in user_config, default_config:
        if os.path.exists(config):
            xml = parseString(open(config).read())
            parse_xmlconfig(xml)
            break
init_vars()
sections_mappings = {
    'additional_eggs': eggs_mappings,
    'plone_zcml': zcml_mappings,
    'plone_products': urls_mappings,
    'plone_np': plone_np_mappings,
    'plone_vsp': plone_vsp_mappings,
    'plone_scripts': scripts_mappings,
}

packaged_version = '3.3.3'
class Template(common.Template):

    summary = 'Template for creating a plone3 project'
    python = 'python-2.4'

    def read_vars(self, command=None):
        if command:
            if not command.options.quiet:
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
        vars['plonesite'] = SPECIALCHARS.sub('', vars['project'])
        vars['category'] = 'zope'
        vars['includesdirs'] = ''
        common.Template.pre(self, command, output_dir, vars)
        vars['mode'] = vars['mode'].lower().strip()

        # transforming eggs requirements as lists
        for var in sections_mappings:
            if var in vars:
                vars[var] = [a.strip() for a in vars[var].split(',')]

        # ZODB3 from egg
        vars['additional_eggs'].append('#ZODB3 is installed as an EGG!')
        vars['additional_eggs'].append('ZODB3')

        # plone system dependencies
        if vars['inside_minitage']:
            for i in ['libxml2', 'libxslt', 'pilwotk', 'libiconv']:
                vars['opt_deps'] += ' %s' %  search_latest('%s.*' % i, vars['minilays'])

        # databases
        minitage_dbs = ['mysql', 'postgresql']
        for db in minitage_dbs:
            if vars['with_database_%s' % db] and vars['inside_minitage']:
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

        for section in sections_mappings:
            for var in [k for k in sections_mappings[section] if vars[k]]:
                if not section == 'plone_zcml':
                    vars[section].append('#%s'%var)
                for item in sections_mappings[section][var]:
                   if section == 'plone_zcml':
                       item = '-'.join(item)
                   if not '%s\n' % item in vars[section]:
                       if not item in vars[section]:
                           vars[section].append(item)



        package_slug_re = re.compile('(.*)-(meta|configure|overrides)', reflags)
        def zcmlsort(obja, objb):
            obja = re.sub('^#', '', obja).strip()
            objb = re.sub('^#', '', objb).strip()
            ma, mb = package_slug_re.match(obja), package_slug_re.match(objb)
            if not obja:
                return 1
            if not objb:
                return -1
            apackage, aslug = (obja, 'configure')
            if ma:
                apackage, aslug = ma.groups()
            bpackage, bslug = (objb, 'configure')
            if mb:
                bpackage, bslug = mb.groups()
            aorder = zcml_loading_order.get((apackage, aslug), 50000)
            border = zcml_loading_order.get((bpackage, bslug), 50000)
            return aorder - border

        # order zcml
        vars["plone_zcml"].sort(zcmlsort)
        vars["plone_zcml"] = [a for a in  vars["plone_zcml"] if a.strip()]

        # add option marker
        for option in zcml_mappings:
            for p in zcml_mappings[option]:
                id = '-'.join(p)
                if id in vars['plone_zcml']:
                    i = vars['plone_zcml'].index(id)
                    vars['plone_zcml'][i:i] = ['#%s' % option]
        vars['plone_zcml'][0:0] = ['']

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
            def null(a, b, c):
                pass
            p3.post = null
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

sd_str = '%s' % (
    'Singing & Dancing NewsLetter, see http://plone.org/products/dancing'
    ' S&D is known to lead to multiple buildout installation errors.'
    ' Be sure to activate it and debug the errors. y/n'
)
Template.vars = common.Template.vars \
        + [var('plone_version', 'Plone version, default is the one supported and packaged', default = packaged_version,),
           var('address', 'Address to listen on', default = 'localhost',),
           var('http_port', 'Port to listen to', default = '8081',),
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
           var('plone_products', 'comma separeted list of adtionnal products to install: eg: file://a.tz file://b.tgz', default = '',),
           var('additional_eggs', 'comma separeted list of additionnal eggs to install', default = '',),
           var('plone_zcml', 'comma separeted list of eggs to include for searching ZCML slugs', default = '',),
           var('plone_np', 'comma separeted list of nested packages for products distro part', default = '',),
           var('plone_vsp', 'comma separeted list of versionned suffix packages for product distro part', default = '',),
           var('plone_scripts', 'comma separeted list of scripts to generate from installed eggs', default = '',),
           var('with_checked_versions', 'Use product versions that interact well together (can be outdated, check [versions] in buildout.', default = 'n',),
           ] + addons_vars

# vim:set et sts=4 ts=4 tw=0:
