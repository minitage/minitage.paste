# Copyright (C) 2009, Mathieu PASQUET <kiorky@cryptelium.net>

__docformat__ = 'restructuredtext en'

from glob import glob
import copy
import os
import shutil
import re

import pkg_resources

from minitage.paste.projects import common


class NoDefaultTemplateError(Exception):
    pass


default_config = pkg_resources.resource_filename(
    'minitage.paste', 'projects/plone3/minitage.plone3.xml')
user_config = os.path.join(os.path.expanduser('~'), '.minitage.plone3.xml')
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
checked_versions_mappings = xmlvars.get(
    'checked_versions_mappings', {})
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
        common.pvar(
            'with_autocheckout_%s' % name,
            description=name,
            default="n",
        )
    )


class Template(common.Template):
    packaged_version = '3.3.5'
    packaged_zope2_version = None
    summary = 'Template for creating a plone3 project'
    python = 'python-2.4'
    init_messages = (
        '%s' % (
            '---------------------------------------------------------\n'
            '\tPlone 3 needs a python 2.4 to run:\n'
            '\t * if you do not fill anything, it will '
            'use minitage or system\'s one\n'
            '\t * if you do not provide one explicitly, '
            'it will use minitage or system\'s one\n'
            '\tAditionnaly you ll got two buildouts for '
            'production (buildout.cfg) and develoment mode (dev.cfg).\n'
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
    qi_mappings = qi_mappings
    qi_hidden_mappings = qi_hidden_mappings
    gs_mappings = gs_mappings
    z2packages = z2packages
    z2products = z2products
    addons_vars = common.get_ordered_discovered_options(addons_vars.values())
    eggs_mappings = eggs_mappings
    scripts_mappings = scripts_mappings
    zcml_loading_order = zcml_loading_order
    zcml_mappings = zcml_mappings
    versions_mappings = versions_mappings
    checked_versions_mappings = checked_versions_mappings
    urls_mappings = urls_mappings
    plone_np_mappings = plone_np_mappings
    plone_vsp_mappings = plone_vsp_mappings
    plone_sources = plone_sources

    def read_vars(self, command=None):
        if command:
            if not command.options.quiet:
                for msg in getattr(self, 'init_messages', []):
                    print msg
        vars = common.Template.read_vars(self, command)
        for i, var in enumerate(vars[:]):
            if var.name in ['deliverance_project'] and command:
                sane_name = common.SPECIALCHARS.sub('', command.args[0])
                vars[i].default = sane_name
            if var.name in ['reverseproxy_host'] and command:
                sane_name = '%s.localhost' % common.SPECIALCHARS.sub(
                    '', command.args[0])
                vars[i].default = sane_name
        return vars

    def get_sources_url(self, cvars=None):
        if not cvars:
            cvars = {}
        v = cvars.get('plone_version', self.packaged_version)
        sources = 'http://dist.plone.org/release/%s/sources.cfg' % v
        return sources

    def pre(self, command, output_dir, vars):
        """register catogory, and roll in common,"""
        vars['mode'] = 'zeo'
        if not 'with_ploneproduct_paasync' in vars:
            vars['with_ploneproduct_paasync'] = False
        if not 'with_ploneproduct_fss' in vars:
            vars['with_ploneproduct_fss'] = False
        #if vars['with_ploneproduct_ploneappblob']:
        #    vars['with_ploneproduct_fss'] = False
        vars['plonesite'] = 'Plone'
        vars['major'] = int(vars['plone_version'][0])
        vars['sources_url'] = self.get_sources_url(vars)
        #vars['versions_url'] = self.get_versions_url(vars)
        #vars['zope2_url'] = self.get_zope2_url(vars)
        #vars['ztk_url'] = self.get_ztk_url(vars)
        if not vars.get('ztk_url', None):
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
                    if (
                        (True in [vars.get(o, False)
                                  for o in self.plone_sources[var]['options']])
                        and (self.plone_sources[var]['name']
                             not in vars['autocheckout'])
                    ):
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

        if not vars['mode'] in ['zeo']:
            raise Exception('Invalid mode (not in zeo')
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        for section in self.sections_mappings:
            for var in [k
                        for k in self.sections_mappings[
                            section]
                        if vars.get(k, '')]:
                # skip plone products which are already in
                # the product 's setup.py
                if vars['with_generic'] and section == 'additional_eggs':
                    pass
                if not section == 'plone_zcml':
                    vars[section].append('#%s' % var)
                for item in self.sections_mappings[section][var]:
                    if section == 'plone_zcml':
                        item = '-'.join(item)
                    if not '%s\n' % item in vars[section]:
                        if not item in vars[section]:
                            vars[section].append(item)

        package_slug_re = re.compile(
            '(.*)-(meta|configure|overrides)', common.reflags)

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
        vars["plone_zcml"] = [a for a in vars["plone_zcml"] if a.strip()]

        # add option marker
        for option in self.zcml_mappings:
            for p in self.zcml_mappings[option]:
                id = '-'.join(p)
                if id in vars['plone_zcml']:
                    i = vars['plone_zcml'].index(id)
                    vars['plone_zcml'][i:i] = ['#%s' % option]
        vars['plone_zcml'][0:0] = ['']

        if not os.path.exists(self.output_dir):
            self.makedirs(self.output_dir)
        # install also the official template from
        # ZopeSkel, setting its variables
        vars['plone_products_install'] = ''
        vars['zope2_install'] = ''
        vars['debug_mode'] = 'off'
        vars['verbose_security'] = 'off'

        # running default template (like plone3_buildout)
        # and getting stuff from it.
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
            print 'Error executing plone3 buildout, %s' % e
        self.post_default_template_hook(command, output_dir, vars, ep)

        # be sure our special python is in priority
        vars['opt_deps'] = re.sub('\s*%s\s*' % self.python, ' ',
                                  vars['opt_deps'])
        vars['opt_deps'] += " %s" % self.python

        for port in range(500):
            vars['http_port%s' % port] = int(
                vars['http_port']) + port
        #if 'socket' == vars['zeo_port'].strip():
        #    vars['zeo_port_buildbot'] = int(vars['zeo_port']) + 1
        vars['running_user'] = common.running_user
        vars['instances_description'] = common.INSTANCES_DESCRIPTION % vars
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
        vars['default_plone_profile'] = '%s.policy:default' % vars['project']
        if vars['with_generic_addon']:
            vars['default_plone_profile'] = '%s:default' % vars['project']
        vars['ndot'] = '.'

    def post(self, command, output_dir, vars):
        common.Template.post(self, command, output_dir, vars)
        os.rename(os.path.join(vars['path'], 'gitignore'),
                  os.path.join(vars['path'], '.gitignore'))
        for f in glob(os.path.join(output_dir, 'scripts/*')):
            os.chmod(f, 0700)

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
plone_vars = [
    common.pvar('address',
                'Address to listen on', default='localhost',),
    common.pvar('http_port',
                'Port to listen to', default='8081',),
    common.pvar('zeo_host',
                'Address for the zeoserver (zeo mode only)',
                default='localhost',),
    common.pvar('with_zeo_socket',
                'Use socket for zeo, y/n', default='n',),
    common.pvar('zope_user',
                'Administrator login', default='admin',),
    common.pvar('zope_password',
                'Admin Password in the ZMI', default='secret',),
    common.pvar('with_cache_support',
                'Proxy cache (varnish)  support y/n', default='y',),
    common.pvar('with_supervisor',
                'Supervisor support (monitoring), '
                'http://supervisord.org/ y/n', default='y',),
    common.pvar('with_supervisor_instance1',
                'Supervisor will automaticly '
                'launch instance 1 in production mode  y/n', default='y',),
    common.pvar('with_supervisor_instance2',
                'Supervisor will automaticly '
                'launch instance 2 in production mode, y/n', default='n',),
    common.pvar('with_supervisor_instance3',
                'Supervisor will automaticly '
                'launch instance 3 in production mode, y/n', default='n',),
    common.pvar('with_supervisor_instance4',
                'Supervisor will automaticly '
                'launch instance 4 in production mode, y/n', default='n',),
    common.pvar('with_haproxy',
                'haproxy support (loadbalancing), '
                'http://haproxy.1wt.eu/ y/n', default='y',),
    common.pvar('plone_products',
                'comma separeted list of adtionnal products '
                'to install: eg: file://a.tz file://b.tgz', default='',),
    common.pvar('additional_eggs',
                'comma separeted list of additionnal eggs to install',
                default='',),
    common.pvar('plone_zcml',
                'comma separeted list of eggs to include for '
                'searching ZCML slugs', default='',),
    common.pvar('plone_np',
                'comma separeted list of nested packages for '
                'products distro part', default='',),
    common.pvar('plone_vsp',
                'comma separeted list of versionned suffix '
                'packages for product distro part', default='',),
    common.pvar('plone_scripts',
                'comma separeted list of scripts to '
                'generate from installed eggs', default='',),
    common.pvar('with_checked_versions',
                'Use product versions that interact '
                'well together (can be outdated, check '
                '[versions] in buildout.', default='n',),
    common.pvar('with_no_zcml',
                'Do not include zcml information', default='n',),
    common.pvar('with_generic',
                'with_generic', default='n',),
    common.pvar('with_generic_addon',
                'with_generic_addon', default='n',),
]

Template.vars = (
    common.Template.vars + [
        common.pvar('plone_version',
             'Plone version, default is the one supported and packaged',
             default=Template.packaged_version,),
    ] +
    plone_vars + Template.addons_vars + dev_vars
)

# vim:set et sts=4 ts=4 tw=0:
