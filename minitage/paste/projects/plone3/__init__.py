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

from glob import glob
import copy
import os
import shutil
import re
import urllib2

import pkg_resources

from iniparse import ConfigParser

from minitage.paste.projects import common
from minitage.paste.common import var as pvar
from minitage.core.common  import search_latest

class NoDefaultTemplateError(Exception): pass

default_config = pkg_resources.resource_filename('minitage.paste', 'projects/plone3/minitage.plone3.xml')
user_config = os.path.join( os.path.expanduser('~'), '.minitage.plone3.xml')
xmlvars = common.read_vars(default_config, user_config)
# plone quickinstaller option/names mappings
qi_mappings = xmlvars.get('qi_mappings', {})
qi_hidden_mappings = xmlvars.get('qi_hidden_mappings', {})
gs_mappings = xmlvars.get('gs_mappings', {})
# eggs registered as Zope2 packages
z2packages = xmlvars.get('z2packages', {})
z2products = xmlvars.get('z2products', {})
# variables discovered via configuration
addons_vars = xmlvars.get('addons_vars', {})
# mappings option/eggs to install
eggs_mappings = xmlvars.get('eggs_mappings', {})
# scripts to generate
scripts_mappings = xmlvars.get('scripts_mappings', {})
# mappings option/zcml to install
zcml_loading_order = xmlvars.get('zcml_loading_order', {})
zcml_mappings = xmlvars.get('zcml_mappings', {})
# mappings option/versions to pin
versions_mappings = xmlvars.get('versions_mappings', {})
# mappings option/versions to pin if the user wants really stable sets
checked_versions_mappings = xmlvars.get('checked_versions_mappings',{})
# mappings option/productdistros to install
urls_mappings = xmlvars.get('urls_mappings', {})
# mappings option/nested packages/version suffix packages  to install
plone_np_mappings = xmlvars.get('plone_np_mappings', {})
plone_vsp_mappings = xmlvars.get('plone_vsp_mappings', {})
plone_sources = xmlvars.get('plone_sources', {})
dev_desc = 'Install %s in development mode.'
dev_vars = []
sources_k = plone_sources.keys()
sources_k.sort()
for name in sources_k:
    dev_vars.append(
        pvar(
            'with_autocheckout_%s' % name,
            description = name,
            default = "n",
        )
    )

class Template(common.Template):
    packaged_version = '3.3.5'
    packaged_zope2_version = None
    summary                    = 'Template for creating a plone3 project'
    python                     = 'python-2.4'
    init_messages = (
        '%s' % (
            '---------------------------------------------------------\n'
            '\tPlone 3 needs a python 2.4 to run:\n'
            '\t * if you do not fill anything, it will use minitage or system\'s one\n'
            '\t * if you do not provide one explicitly, it will use minitage or system\'s one\n'
            '\t * Bindings will be automaticly included when you choose for example relstorage/mysql or plone ldap support.\n'
            '\tAditionnaly you ll got two buildouts for production (buildout.cfg) and develoment mode (dev.cfg).\n'
            '\tYou can also activate or safely ignore questions about zeoserver and relstorage if you do not use them.\n'
            '---------------------------------------------------------\n'
        ),
    )
    # not nice, but allow us to import variables from another place like
    # from plone3 import qi_mappings and also avoid template copy/paste,
    # just inherit and redefine those variables in the child class.
    # plone quickinstaller option/names mappings

    # buildout <-> minitage config vars mapping
    sections_mappings = {
        'additional_eggs': eggs_mappings,
        'plone_zcml': zcml_mappings,
        'plone_products': urls_mappings,
        'plone_np': plone_np_mappings,
        'plone_vsp': plone_vsp_mappings,
        'plone_scripts': scripts_mappings,
    }
    qi_mappings               = qi_mappings
    qi_hidden_mappings        = qi_hidden_mappings
    gs_mappings               = gs_mappings
    z2packages                = z2packages
    z2products                = z2products
    addons_vars               = common.get_ordered_discovered_options(addons_vars.values())
    eggs_mappings             = eggs_mappings
    scripts_mappings          = scripts_mappings
    zcml_loading_order        = zcml_loading_order
    zcml_mappings             = zcml_mappings
    versions_mappings         = versions_mappings
    checked_versions_mappings = checked_versions_mappings
    urls_mappings             = urls_mappings
    plone_np_mappings         = plone_np_mappings
    plone_vsp_mappings        = plone_vsp_mappings
    plone_sources             = plone_sources

    def read_vars(self, command=None):
        if command:
            if not command.options.quiet:
                for msg in getattr(self, 'init_messages', []):
                    print msg
        vars = common.Template.read_vars(self, command)
        for i, var in enumerate(vars[:]):
            if var.name in ['deliverance_project', 'relstorage_dbname', 'relstorage_dbuser'] and command:
                sane_name = common.SPECIALCHARS.sub('', command.args[0])
                vars[i].default = sane_name
            if var.name in ['reverseproxy_host',] and command:
                sane_name = '%s.localhost' % common.SPECIALCHARS.sub('', command.args[0])
                vars[i].default = sane_name
        return vars

    def get_versions_url(self, cvars=None):
        if not cvars: cvars = {}
        v = cvars.get('plone_version', self.packaged_version)
        url = 'http://dist.plone.org/release/%s/versions.cfg' % v
        return url

    def get_sources_url(self, cvars=None):
        if not cvars: cvars = {}
        v = cvars.get('plone_version', self.packaged_version)
        sources = 'http://dist.plone.org/release/%s/sources.cfg' % v
        return sources

    def get_zope2_url(self, cvars=None):
        if not cvars: cvars = {}
        url, v = None, None
        if self.packaged_zope2_version:
            v = cvars.get('zope2_version', self.packaged_zope2_version)
        url = 'http://download.zope.org/Zope2/index/%s/versions.cfg' % v
        return url

    def get_ztk_url(self, cvars=None):
        if not cvars: cvars = {}
        url, v = None, None
        if getattr(self, 'packaged_ztk_version', False):
            v = cvars.get('ztk_version', getattr(self, 'packaged_ztk_version'))
        url = 'http://download.zope.org/zopetoolkit/index/%s/ztk-versions.cfg' % v
        return url

    def pre(self, command, output_dir, vars):
        """register catogory, and roll in common,"""
        if not 'with_ploneproduct_paasync' in vars:
            vars['with_ploneproduct_paasync'] = False
        if not 'with_ploneproduct_fss' in vars:
            vars['with_ploneproduct_fss'] = False
        #if vars['with_ploneproduct_ploneappblob']:
        #    vars['with_ploneproduct_fss'] = False
        vars['plonesite'] = common.SPECIALCHARS.sub('', vars['project'])
        vars['major'] = int(vars['plone_version'][0])
        vars['versions_url'] = self.get_versions_url(vars)
        vars['sources_url'] = self.get_sources_url(vars)
        vars['zope2_url'] = self.get_zope2_url(vars)
        vars['ztk_url'] = self.get_ztk_url(vars)
        if not vars['ztk_url']:
            vars['ztk_url'] = False
        vars['sane_name'] = common.SPECIALCHARS.sub('', vars['project'])
        vars['category'] = 'zope'
        vars['includesdirs'] = ''
        vars['hr'] = '#' * 120
        common.Template.pre(self, command, output_dir, vars)
        vars['mode'] = vars['mode'].lower().strip()

        # transforming eggs requirements as lists
        for var in self.sections_mappings:
            if var in vars:
                vars[var] = [a.strip() for a in vars[var].split(',')]

        vars['autocheckout'] = []
        for var in vars:
            if var.startswith('with_autocheckout') and vars[var]:
                vn = var.replace('with_autocheckout_', '')
                vars['autocheckout'].append(
                    self.plone_sources[vn]['name']
                )

        for var in self.plone_sources:
            if self.plone_sources[var].get('autocheckout', '') == 'y':
                if not self.plone_sources[var]['name'] in vars['autocheckout']:
                    if ((True in [vars.get(o, False)
                                  for o in self.plone_sources[var]['options']])
                        and (self.plone_sources[var]['name'] not in vars['autocheckout'])):
                        vars['autocheckout'].append(
                            self.plone_sources[var]['name']
                        )

        lps = copy.deepcopy(self.plone_sources)
        for item in self.plone_sources:
            col = self.plone_sources[item]
            found = False
            for option in col['options']:
                if vars.get(option, False):
                    found = True
                    break
            if not found:
                del lps[item]
        vars['plone_sources'] = lps

        # ZODB3 from egg
        if vars['major'] < 4:
            vars['additional_eggs'].append('#ZODB3 is installed as an EGG!')
            vars['additional_eggs'].append('ZODB3')

        # plone system dependencies
        if vars['inside_minitage']:
            for i in ['libxml2', 'libxslt', 'pil-1', 'libiconv']:
                vars['opt_deps'] += ' %s' %  search_latest('%s.*' % i, vars['minilays'])

        # databases
        minitage_dbs = ['mysql', 'postgresql']
        for db in minitage_dbs:
            if vars['with_database_%s' % db] and vars['inside_minitage']:
                vars['opt_deps'] += ' %s' % search_latest('%s-\d\.\d*'% db, vars['minilays'])
        # databases
        if vars['with_binding_mapscript'] and vars['inside_minitage']:
            vars['opt_deps'] += ' %s' % search_latest('mapserver-\d\.\d*', vars['minilays'])
        # collective.geo
        if 'with_ploneproduct_cgeo' in vars:
            if vars['with_ploneproduct_cgeo'] and vars['inside_minitage']:
                for i in ('geos-\d\.\d*','gdal-\d\.\d*'):
                    vars['opt_deps'] += ' %s' % search_latest(i, vars['minilays'])
        # tesseact
        if vars['with_binding_tesseract'] and vars['inside_minitage']:
            for i in ('tesseract-\d','leptonica-\d'):
                vars['opt_deps'] += ' %s' % search_latest(i, vars['minilays'])
        # pyqt
        vars['pyqt'] = ''
        if vars['with_binding_pyqt'] and vars['inside_minitage']:
            vars['opt_deps'] += ' %s' % search_latest('swiglib-\d\.\d+', vars['minilays'])
            for i in ('pyqt-\d\.\d+','sip-\d\.\d+'):
                vars['opt_deps'] += ' %s' % search_latest(i, vars['minilays'])
                vars['pyqt'] += '\n   %s' %  (
                    '${buildout:directory}/../../'
                    'eggs/%s/parts'
                    '/site-packages-%s/site-packages-%s' % (
                        search_latest(i, vars['minilays']),
                        vars['pyver'],
                        vars['pyver'],
                    )
                )

        # openldap
        if vars['with_binding_ldap'] and vars['inside_minitage']:
            cs = search_latest('cyrus-sasl-\d\.\d*', vars['minilays'])
            vars['opt_deps'] += ' %s %s %s' % (
                search_latest('openldap-\d\.\d*', vars['minilays']),
                search_latest('openssl-1', vars['minilays']),
                cs
            )
            vars['includesdirs'] = '\n    %s'%  os.path.join(
                vars['mt'], 'dependencies', cs, 'parts', 'part', 'include', 'sasl'
            )

        # haproxy
        if vars['with_haproxy'] and vars['inside_minitage']:
            vars['opt_deps'] += ' %s' % search_latest('haproxy-\d\.\d*', vars['minilays'])
        # htmldoc
        if vars['with_ploneproduct_awspdfbook'] and vars['inside_minitage']:
            vars['opt_deps'] += ' %s' % search_latest('htmldoc-\d\.\d*', vars['minilays'])

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
        pin_added = []
        for var in self.versions_mappings:
            vars['plone_versions'].append(('# %s' % var, '',))
            vmap = self.versions_mappings[var]
            vmap.sort()
            for pin in vmap:
                if not pin in pin_added:
                    pin_added.append(pin)
                    vars['plone_versions'].append(pin)

        if vars["with_checked_versions"]:
            for var in self.checked_versions_mappings:
                if vars.get(var, False):
                    vars['plone_versions'].append(('# %s' % var, '',))
                    vmap = self.checked_versions_mappings[var].keys()
                    vmap.sort()
                    for kpin in vmap:
                        pin = (kpin, self.checked_versions_mappings[var][kpin])
                        if not pin in pin_added:
                            pin_added.append(pin)
                            vars['plone_versions'].append(pin)

        if not vars['mode'] in ['zodb', 'relstorage', 'zeo']:
            raise Exception('Invalid mode (not in zeo, zodb, relstorage')
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        for section in self.sections_mappings:
            for var in [k for k in self.sections_mappings[section] if vars.get(k, '')]:
                # skip plone products which are already in the product 's setup.py
                if vars['with_generic'] and var.startswith('with_ploneproduct') and section == 'additional_eggs':
                    continue
                if not section == 'plone_zcml':
                    vars[section].append('#%s'%var)
                for item in self.sections_mappings[section][var]:
                   if section == 'plone_zcml':
                       item = '-'.join(item)
                   if not '%s\n' % item in vars[section]:
                       if not item in vars[section]:
                           vars[section].append(item)


        package_slug_re = re.compile('(.*)-(meta|configure|overrides)', common.reflags)
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
            aorder = self.zcml_loading_order.get((apackage, aslug), 50000)
            border = self.zcml_loading_order.get((bpackage, bslug), 50000)
            return aorder - border

        # order zcml
        vars["plone_zcml"].sort(zcmlsort)
        vars["plone_zcml"] = [a for a in  vars["plone_zcml"] if a.strip()]

        # add option marker
        for option in self.zcml_mappings:
            for p in self.zcml_mappings[option]:
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

        # running default template (like plone3_buildout) and getting stuff from it.
        ep = None
        try:
            if not getattr(self, 'default_template_package', None):
                raise NoDefaultTemplateError('')

            epk = pkg_resources.load_entry_point(
                self.default_template_package,
                self.default_template_epn,
                self.default_template_templaten
            )
            ep = epk(self)
            coo = command.options.overwrite
            command.options.overwrite = True
            def null(a, b, c):
                pass
            ep.post = null
            ep.check_vars(vars, command)
            ep.run(command, vars['path'], vars)
            command.options.overwrite = coo
        except NoDefaultTemplateError, e:
            pass
        except Exception, e:
            print 'Error executing plone3 buildout, %s'%e
        self.post_default_template_hook(command, output_dir, vars, ep)

        # be sure our special python is in priority
        vars['opt_deps'] = re.sub('\s*%s\s*' % self.python, ' ', vars['opt_deps'])
        vars['opt_deps'] += " %s" % self.python
        vars['http_port1'] = int(vars['http_port']) + 1
        vars['http_port2'] = int(vars['http_port']) + 2
        vars['http_port3'] = int(vars['http_port']) + 3
        vars['http_port4'] = int(vars['http_port']) + 4
        vars['http_port5'] = int(vars['http_port']) + 5
        vars['http_port_buildbot'] = int(vars['http_port']) + 6
        vars['http_port6'] = int(vars['http_port']) + 7
        vars['http_port7'] = int(vars['http_port']) + 8
        vars['http_port9'] = int(vars['http_port']) + 9
        vars['zeo_port_buildbot'] = ''
        if 'socket' == vars['zeo_port'].strip():
            vars['zeo_port_buildbot'] = int(vars['zeo_port']) + 1
        vars['running_user'] = common.running_user
        vars['instances_description'] = common.INSTANCES_DESCRIPTION % vars
        if not vars['reverseproxy_aliases']:
            vars['reverseproxy_aliases'] = ''
        vars['sreverseproxy_aliases'] = vars['reverseproxy_aliases'].split(',')
        suffix = vars['major']
        if vars['major'] > 3:
            suffix = self.name.replace('minitage.plone', '')
        zaztk_path = pkg_resources.resource_filename(
            'minitage.paste',
            'projects/plone%s/zopeapp.versions.cfg' % suffix
        )
        ztk_path = pkg_resources.resource_filename(
            'minitage.paste',
            'projects/plone%s/ztk.versions.cfg' % suffix
        )
        vars['have_ztk'] = False
        if os.path.exists(ztk_path):
            vars['have_ztk'] = True
            vars['ztk_path'] = ztk_path
            vars['zaztk_path'] = zaztk_path
        vars['default_plone_profile'] =  '%s.policy:default' % vars['project']
        if vars['with_generic_addon']:
            vars['default_plone_profile'] =  '%s:default' % vars['project']
        vars['ndot'] = '.'

    def post(self, command, output_dir, vars):
        common.Template.post(self, command, output_dir, vars)
        etc = os.path.join(vars['path'], 'etc', 'plone')
        if not os.path.isdir(etc):
            os.makedirs(etc)
        cfg = os.path.join(vars['path'], 'etc', 'base.cfg')
        dst = os.path.join(vars['path'],
                           'etc', 'plone', 'plone%s.buildout.cfg' % vars['major'])
        vdst = os.path.join(vars['path'],
                           'etc', 'plone', 'plone%s.versions.cfg' % vars['major'])
        sdst = os.path.join(vars['path'],
                           'etc', 'plone', 'plone%s.sources.cfg' % vars['major'])
        ztkdst = os.path.join(vars['path'], 'etc', 'plone', 'ztk.versions.cfg')
        zaztkdst = os.path.join(vars['path'], 'etc', 'plone', 'zopeapp.versions.cfg')
        zdst = os.path.join(vars['path'],
                            'etc', 'plone', 'zope2.versions.cfg')
        os.rename(os.path.join(vars['path'], 'gitignore'),
                  os.path.join(vars['path'], '.gitignore'))
        bc = ConfigParser()
        bc.read(cfg)

        for f in (glob(os.path.join(output_dir, 'scripts/*'))
                  + glob(os.path.join(output_dir, 'etc/hudson/%s/build/*' % vars['project']))
                 ):
            os.chmod(f, 0700)
        # release KGS
        #try:
        #    open(vdst, 'w').write(
        #        urllib2.urlopen(vars['versions_url']).read()
        #    )
        #except Exception, e:
        suffix = vars['major']
        if vars['major'] > 3:
            suffix = self.name.replace('minitage.plone', '')
        shutil.copy2(
            pkg_resources.resource_filename(
                'minitage.paste',
                'projects/plone%s/versions.cfg' % suffix
            ),
            vdst
        )
            #self.lastlogs.append(
            #    "Versions have not been fixed, be ware. Are"
            #    " you connected to the internet (%s).\n" % e
            #)
            #self.lastlogs.append(
            #    "%s" % (
            #        'As a default, we will take an already'
            #        ' downloaded versions.cfg matching plone'
            #        ' %s.\n' %
            #        self.packaged_version
            #    )
            #)
        # zope2 KGS
        if vars['have_ztk'] == True:
            shutil.copy2(vars['ztk_path'], ztkdst)
            shutil.copy2(vars['zaztk_path'], zaztkdst)

        if vars['major'] > 3:
            #try:
            #    open(zdst, 'w').write(
            #        urllib2.urlopen(vars['zope2_url']).read()
            #    )
            #    raise
            #except Exception, e:
            shutil.copy2(
                pkg_resources.resource_filename(
                    'minitage.paste',
                    'projects/plone%s/zope2.versions.cfg' % suffix
                ),
                zdst
            )

        # release mr.developer config
        #try:
        #    open(sdst, 'w').write(
        #        urllib2.urlopen(vars['sources_url']).read()
        #    )
        #except Exception, e:
        shutil.copy2(
            pkg_resources.resource_filename(
                'minitage.paste',
                'projects/plone%s/sources.cfg' % suffix
            ),
            sdst
        )
        #    if vars['major'] > 3:
        #        self.lastlogs.append(
        #            "Sources have not been fixed, be ware. Are"
        #            " you connected to the internet (%s).\n" % e
        #        )



    def post_default_template_hook(self, command, output_dir, vars, ep):
        """No more used."""
        pass


def get_packaged_version(Template):
    return getattr(Template, 'packaged_version')
sd_str = '%s' % (
    'Singing & Dancing NewsLetter, see http://plone.org/products/dancing'
    ' S&D is known to lead to multiple buildout installation errors.'
    ' Be sure to activate it and debug the errors. y/n'
)
plone_vars = [pvar('address', 'Address to listen on', default = 'localhost',),
              pvar('http_port', 'Port to listen to', default = '8081',),
              pvar('mode', 'Mode to use : zodb|relstorage|zeo', default = 'zeo'),
              pvar('devmode', 'Mode to use in development mode: zodb|relstorage|zeo', default = 'zeo'),
              pvar('zeo_host', 'Address for the zeoserver (zeo mode only)', default = 'localhost',),
              pvar('zeo_port', 'Port for the zeoserver (zeo mode only)', default = '8100',),
              pvar('with_zeo_socket', 'Use socket for zeo, y/n', default = 'n',),
              pvar('zope_user', 'Administrator login', default = 'admin',),
              pvar('zope_password', 'Admin Password in the ZMI', default = 'secret',),
              pvar('relstorage_type', 'Relstorage database type (only useful for relstorage mode)', default = 'postgresql',),
              pvar('relstorage_host', 'Relstorage database host (only useful for relstorage mode)', default = 'localhost',),
              pvar('relstorage_port', 'Relstorage databse port (only useful for relstorage mode). (postgresql : 5432, mysql : 3306)', default = '5432',),
              pvar('relstorage_dbname', 'Relstorage database name (only useful for relstorage mode)', default = 'minitagedb',),
              pvar('relstorage_dbuser', 'Relstorage user (only useful for relstorage mode)', default = common.running_user),
              pvar('relstorage_password', 'Relstorage password (only useful for relstorage mode)', default = 'secret',),
              pvar('solr_host', 'Solr host (only useful if you want solr)', default = '127.0.0.1',),
              pvar('solr_port', 'Solr port (only useful if you want solr)', default = '8983',),
              pvar('solr_path', 'Solr path (only useful if you want solr)', default = '/solr',),
              pvar('staging_host', 'Host to get a datafs from address', default = 'host',),
              pvar('staging_user', 'User for connecting to the staging host', default = 'user',),
              pvar('staging_path', 'Path to the buildout root on the staging host', default = '/',),
              pvar('supervisor_host', 'Supervisor host', default = '127.0.0.1',),
              pvar('supervisor_port', 'Supervisor port', default = '9001',),
              pvar('supervisor_user', 'Supervisor web user', default = 'admin',),
              pvar('supervisor_password', 'Supervisor web password', default = 'secret',),
              pvar('with_supervisor', 'Supervisor support (monitoring), http://supervisord.org/ y/n', default = 'y',),
              pvar('with_supervisor', 'Supervisor support (monitoring), http://supervisord.org/ y/n', default = 'y',),
              pvar('with_supervisor_instance1', 'Supervisor will automaticly launch instance 1 in production mode  y/n', default = 'y',),
              pvar('with_supervisor_instance2', 'Supervisor will automaticly launch instance 2 in production mode, y/n', default = 'n',),
              pvar('with_supervisor_instance3', 'Supervisor will automaticly launch instance 3 in production mode, y/n', default = 'n',),
              pvar('with_supervisor_instance4', 'Supervisor will automaticly launch instance 4 in production mode, y/n', default = 'n',),
              pvar('buildbot_master_web_port', 'Buildbot master web port', default = '9080',),
              pvar('buildbot_master_control_port', 'Buildbot master control port', default = '9081',),
              pvar('buildbot_master_host', 'Buildbot master host', default = '127.0.0.1',),
              pvar('buildbot_slave_password',  'Buildbot password', default = 'i_am_a_buildbot_slave_password',),
              pvar('buildbot_cron',  'Buildbot cron to schedule builds', default = '0 3 * * *',),
              pvar('with_haproxy', 'haproxy configuration file generation support (loadbalancing), http://haproxy.1wt.eu/ y/n', default = 'n',),
              pvar('haproxy_host', 'Haproxy host', default = '127.0.0.1',),
              pvar('haproxy_port', 'Haproxy port', default = '8201',),
              pvar('plone_products', 'comma separeted list of adtionnal products to install: eg: file://a.tz file://b.tgz', default = '',),
              pvar('additional_eggs', 'comma separeted list of additionnal eggs to install', default = '',),
              pvar('plone_zcml', 'comma separeted list of eggs to include for searching ZCML slugs', default = '',),
              pvar('plone_np', 'comma separeted list of nested packages for products distro part', default = '',),
              pvar('plone_vsp', 'comma separeted list of versionned suffix packages for product distro part', default = '',),
              pvar('plone_scripts', 'comma separeted list of scripts to generate from installed eggs', default = '',),
              pvar('with_checked_versions', 'Use product versions that interact well together (can be outdated, check [versions] in buildout.', default = 'n',),
              pvar('with_no_zcml', 'Do not include zcml information', default = 'n',),
              pvar('with_generic', 'with_generic', default = 'n',),
              pvar('with_generic_addon', 'with_generic_addon', default = 'n',),
             ]

Template.vars = common.Template.vars +\
        [pvar('plone_version', 'Plone version, default is the one supported and packaged', default = Template.packaged_version,),]+\
        plone_vars + \
        Template.addons_vars +\
        dev_vars

# vim:set et sts=4 ts=4 tw=0:
