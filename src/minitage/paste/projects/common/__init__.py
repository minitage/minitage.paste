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

import sys
import os
import re
import subprocess
import getpass
import copy
import pwd, getpass, grp

import pkg_resources

from xml.dom.minidom import parse, parseString
from minitage.paste import common
from minitage.core.common import which, search_latest

from minitage.paste.common import running_user, gid, group

reflags = re.M | re.U | re.S
UNSPACER = re.compile('\s+|\n', reflags)
SPECIALCHARS = common.SPECIALCHARS
INSTANCES_DESCRIPTION = """"""


class Template(common.Template):
    """Common template"""

    def post(self, command, output_dir, vars):
        self.lastlogs.append(
            '* A project has been created in %s.\n' % vars['path']
        )
        return common.Template.post(self, command, output_dir, vars)

    def pre(self, command, output_dir, vars):
        common.Template.pre(self, command, output_dir, vars)
        vars['path'] = self.output_dir
        vars['sharp'] = '#'
        vars['linux'] = 'linux' in sys.platform
        if not 'opt_deps' in vars:
            vars['opt_deps'] = ''


Template.vars = common.Template.vars + [
    common.var('scm_type',
               'Minibuild checkout facility'
               ' (git|bzr|hg|svn|static)\n'
               'static can be used for both '
               'http, ftp and file:// uris: '
               '(only useful in a minitage)',
               default='git',),
    common.var('uri',
               'Url of the project to checkout (only useful in a minitage)',
               default='git@gitorious-git.makina-corpus.net/',),
    #common.var('install_method',
    #           'The install method of your minibuild '
    #           '(only useful in a minitage)',
    #           default = 'buildout',),
    common.var('homepage',
               'Homepage url of your project '
               '(only useful in a minitage)',
               default='http://foo.net',),
    #common.var('python',
    #           'the Python interpreter to use. (Only useful if you are not'
    #           'inside a minitage.',
    #           default = sys.executable,),
    common.var('author',
               'Author signature',
               default='%s <%s@localhost>' % (running_user, running_user),),
    common.var('author_email',
               'Author email',
               default='%s@localhost' % (running_user),)
]


def purge_nodes(document=None,
                sectionName=None,
                elementName=None,
                mapping=None,
                key='name',
                peroption=False,
                multiple=False,
                want=False):

    for purge in document.getElementsByTagName('purge'):
        for section in purge.getElementsByTagName(sectionName):
            for node in section.getElementsByTagName(elementName):
                oattrs = dict(node.attributes.items())
                names = oattrs.get(key, '').split(',')
                for name in names:
                    if name:
                        if name in mapping:
                            if sectionName == 'versions' and ('p' in oattrs):
                                infos = (oattrs['p'], oattrs['v'])
                                if infos in mapping:
                                    mapping.pop(mapping.index(infos))
                                if infos in mapping[name]:
                                    mapping[name].pop(mapping[name].index(
                                        infos))
                            else:
                                del mapping[name]
                        elif sectionName == 'gs':
                            indexes = dict(
                                [(k[0], k)
                                 for k in mapping.keys()])
                            if name in indexes:
                                del mapping[indexes[name]]

                        else:
                            opts = oattrs.get('options', '').split(',')
                            for opt in opts:
                                if opt in mapping:
                                    found = False
                                    if name in mapping[opt]:
                                        found = True
                                    nname = oattrs.get('name', '').strip()
                                    if key in ['zproduct', 'zpackage']:
                                        name = nname
                                        if sectionName == 'miscproducts':
                                            name = oattrs.get(key, '')
                                        if name in mapping[opt]:
                                            found = True
                                    if key == 'zcml':
                                        for a in mapping[opt]:
                                            msp_str = 'miscproducts'
                                            if(
                                                (name == a[1]
                                                 and sectionName != msp_str)
                                                or(nname == a[0]
                                                   and a[1]
                                                   in oattrs.get('zcml')
                                                   and sectionName == msp_str)
                                            ):
                                                name = a
                                                found = True
                                                break
                                    if found:
                                        if isinstance(mapping[opt], dict):
                                            del mapping[opt][name]
                                        else:
                                            mapping[opt].pop(
                                                mapping[opt].index(name))

    return []


def get_ordered_discovered_options(discovered_options):
    discovered_options.sort(lambda x, y: x[0] - y[0])
    return [o[1] for o in discovered_options]


def parse_xmlconfig(xml,
                    base_vars = None,
                    purge=None,
                   ):
    """Parse a minitage paster configuration file,
    mainly used in plone templates."""
    result = {
        'qi_mappings' :                  {},
        'qi_hidden_mappings' :           {},
        'gs_mappings' :                  {},
        'z2packages' :                   {},
        'z2products' :                   {},
        'addons_vars' :                  {},
        'eggs_mappings' :                {},
        'scripts_mappings' :             {},
        'zcml_loading_order' :           {},
        'zcml_mappings' :                {},
        'versions_mappings' :            {},
        'checked_versions_mappings' :    {},
        'urls_mappings' :                {},
        'plone_np_mappings' :            {},
        'plone_vsp_mappings' :           {},
        'plone_sources' :                {},
        'framework_apps' :               {},
    }
    overrides = False
    if base_vars:
        overrides = True
        if purge is None:
            purge = True
        result.update(copy.deepcopy(base_vars))
    qi_mappings = result.get('qi_mappings')
    z2packages = result.get('z2packages')
    z2products = result.get('z2products')
    addons_vars = result.get('addons_vars')
    eggs_mappings = result.get('eggs_mappings')
    scripts_mappings = result.get('scripts_mappings')
    zcml_loading_order = result.get('zcml_loading_order')
    zcml_mappings = result.get('zcml_mappings')
    gs_mappings = result.get('gs_mappings')
    qi_hidden_mappings = result.get('qi_hidden_mappings')
    versions_mappings = result.get('versions_mappings')
    checked_versions_mappings = result.get('checked_versions_mappings')
    urls_mappings = result.get('urls_mappings')
    plone_np_mappings = result.get('plone_np_mappings')
    plone_vsp_mappings = result.get('plone_vsp_mappings')
    plone_sources = result.get('plone_sources')
    framework_apps = result.get('framework_apps')
    # discover  additionnal configuration options
    if purge:
        purge_nodes(xml, 'options', 'option', addons_vars)
        purge_nodes(xml, 'versions', 'version',
                    versions_mappings, peroption=True)
        purge_nodes(xml, 'checkedversions', 'version',
                    checked_versions_mappings, 'p', peroption=True)
        purge_nodes(xml, 'sources', 'source', plone_sources)

        purge_nodes(xml, 'qi', 'product', qi_mappings, peroption=True)
        purge_nodes(xml, 'gs', 'product', gs_mappings, peroption=True)
        purge_nodes(xml, 'productdistros', 'productdistro',
                    urls_mappings, key="url", peroption=True)
        purge_nodes(xml, 'eggs', 'egg', eggs_mappings, peroption=True)
        purge_nodes(xml, 'eggs',
                    'egg', scripts_mappings, 'scripts', peroption=True)
        purge_nodes(xml, 'eggs', 'egg', zcml_mappings, 'zcml', peroption=True)
        purge_nodes(xml, 'eggs', 'egg', z2packages, 'zpackage', peroption=True)
        purge_nodes(xml, 'eggs', 'egg', z2products, 'zproduct', peroption=True)
        purge_nodes(xml, 'miscproducts',
                    'product', zcml_mappings, 'zcml', peroption=True)
        purge_nodes(xml, 'miscproducts',
                    'product', z2packages, 'zpackage', peroption=True)
        purge_nodes(xml, 'miscproducts',
                    'product', z2products, 'zproduct', peroption=True)

    xmlTemplate = xml.getElementsByTagName('template')[0]
    try:
        optsnodes = xmlTemplate.getElementsByTagName('options')
        if optsnodes:
            for elem in optsnodes:
                nodes = elem.getElementsByTagName('option')
                for o in nodes:
                    oattrs = dict(o.attributes.items())
                    order = int(oattrs.get('order', 99999))
                    # be sure not to have unicode params
                    # there because paster will swallow them up
                    addons_vars[oattrs.get('name')] = (
                        order,
                        common.var(
                            oattrs.get('name'),
                            UNSPACER.sub(' ',
                                         oattrs.get(
                                             'description', '').strip()),
                            default=oattrs.get('default')
                        )
                    )

        # discover development sources information
        sources_node = xmlTemplate.getElementsByTagName('sources')
        if sources_node:
            for elem in sources_node:
                nodes = elem.getElementsByTagName('source')
                for e in nodes:
                    oattrs = dict(e.attributes.items())
                    options = [option.strip()
                               for option in oattrs['options'].split(',')]
                    name = oattrs.get('name').strip()
                    if overrides or (not name in plone_sources):
                        asegg = ''
                        if oattrs.get('asegg', '').strip():
                            asegg = 'egg=false'
                        spath = ''
                        if oattrs.get('path', '').strip():
                            spath = 'path=%s' % oattrs.get('path', '').strip()
                        item = {
                            'name':     name,
                            'type':     oattrs.get('type').strip(),
                            'url':      oattrs.get('url'),
                            'options': options,
                            'default': oattrs.get('default', '').strip(),
                            'autocheckout': oattrs.get(
                                'autocheckout', '').strip(),
                            'opt_arg': oattrs.get('optarg', '').strip(),
                            'asegg': asegg,
                            'path': spath,
                        }
                        plone_sources[name] = item

        # discover KGS version
        cvs = xmlTemplate.getElementsByTagName('checkedversions')
        if cvs:
            for elem in cvs:
                nodes = elem.getElementsByTagName('version')
                added = []
                for e in nodes:
                    oattrs = dict(e.attributes.items())
                    for option in oattrs['options'].split(','):
                        option = option.strip()
                        if not option in checked_versions_mappings:
                            checked_versions_mappings[option] = {}
                        if 'v' in oattrs:
                            if overrides or (
                                not oattrs['p']
                                in checked_versions_mappings[option]
                            ):
                                if not (option, oattrs['p']) in added:
                                    added.append((option, oattrs['p']))
                                    checked_versions_mappings[
                                        option][oattrs['p']] = oattrs['v']

        # discover andatory versions pinning
        vs = xmlTemplate.getElementsByTagName('versions')
        # versions_mappings = {RelStorage': [('ZODB3', '3.7.2')],}
        if vs:
            for elem in vs:
                nodes = elem.getElementsByTagName('version')
                added = []
                for e in nodes:
                    oattrs = dict(e.attributes.items())
                    for option in oattrs['name'].split(','):
                        option = option.strip()
                        if not option in versions_mappings:
                            versions_mappings[option] = []
                        if 'p' in oattrs:
                            item = (oattrs['p'], oattrs['v'])
                            if overrides or (not item in
                                             versions_mappings[option]):
                                if not item[0] in added:
                                    added.append(item[0])
                                    for index, c in enumerate(
                                        copy.deepcopy(
                                            versions_mappings[option])
                                    ):
                                        if c[0] == item[0]:
                                            del versions_mappings[
                                                option][index]
                                    versions_mappings[option].append(item)

        # quickinstaller mappings discovery
        qi = xmlTemplate.getElementsByTagName('qi')
        if qi:
            for elem in qi:
                nodes = elem.getElementsByTagName('product')
                for e in nodes:
                    oattrs = dict(e.attributes.items())
                    for option in oattrs['options'].split(','):
                        option = option.strip()
                        hidden = 'true' == oattrs.get('hidden', 'true')
                        if hidden and (not option in qi_hidden_mappings):
                            qi_hidden_mappings[option] = []
                        if not hidden and (not option in qi_mappings):
                            qi_mappings[option] = []
                        if hidden and (
                            not oattrs['name'] in qi_hidden_mappings
                        ):
                            qi_hidden_mappings[option].append(oattrs['name'])
                        if not hidden and (not oattrs['name'] in qi_mappings):
                            qi_mappings[option].append(
                                {
                                    'name': oattrs['name'],
                                    'order': int(
                                        oattrs.get('order', '1'.strip()))
                                }
                            )
            # order options
            for option in qi_mappings:
                qi_mappings[option].sort(lambda x, y: -x['order'] + y['order'])

        # genericsetup mappings discovery
        gs = xmlTemplate.getElementsByTagName('gs')
        if gs:
            for elem in gs:
                nodes = elem.getElementsByTagName('product')
                for e in nodes:
                    oattrs = dict(e.attributes.items())
                    for option in oattrs['options'].split(','):
                        option = option.strip()
                        profile = (oattrs['name'],
                                   oattrs.get('profile', 'default'),
                                   int(oattrs.get('order', 99999)))
                        if not profile in gs_mappings:
                            gs_mappings[profile] = []
                        if not option in gs_mappings[profile]:
                            gs_mappings[profile].append(option)

        # eggs/zcml discovery
        eggs = xmlTemplate.getElementsByTagName('eggs')
        if eggs:
            for elem in eggs:
                nodes = elem.getElementsByTagName('egg')
                for e in nodes:
                    oattrs = dict(e.attributes.items())
                    for option in oattrs['options'].split(','):
                        option = option.strip()
                        if not option in eggs_mappings:
                            eggs_mappings[option] = []
                        if (not oattrs['name'] in eggs_mappings[option]):
                            eggs_mappings[option].append(oattrs['name'])
                        if 'app' in oattrs:
                            if (not option in framework_apps):
                                framework_apps[option] = []
                            for item in oattrs['app'].split(','):
                                framework_apps[option].append(item)
                        if 'scripts' in oattrs:
                            if (not option in scripts_mappings):
                                scripts_mappings[option] = []
                            for item in oattrs['scripts'].split(','):
                                scripts_mappings[option].append(item)
                        if 'zcml' in oattrs:
                            if not option in zcml_mappings:
                                zcml_mappings[option] = []
                            for slug in oattrs['zcml'].split(','):
                                item = (oattrs['name'], slug.strip())
                                if overrides or (not item in
                                                 zcml_mappings[option]):
                                    zcml_mappings[option].append(item)
                                    zcml_loading_order[item] = int(
                                        oattrs.get('zcmlorder', '50000')
                                    )
                        for d, package in [(z2packages, 'zpackage'),
                                           (z2products, 'zproduct')]:
                            if package in oattrs:
                                v = oattrs[package]
                                if not option in d:
                                    d[option] = []
                                if v == 'y':
                                    if not oattrs['name'] in d[option]:
                                        d[option].append(oattrs['name'])
                                else:
                                    #d[option].append('#%s' % oattrs['name'])
                                    zp = [z.strip()
                                          for z in oattrs[package].split(',')]
                                    noecho = [d[option].append(z)
                                              for z in zp
                                              if not z in d[option]]
        # misc product discovery
        miscproducts = xmlTemplate.getElementsByTagName('miscproducts')
        if miscproducts:
            for elem in miscproducts:
                nodes = elem.getElementsByTagName('product')
                for e in nodes:
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
                                    zcml_loading_order[item] = int(
                                        oattrs.get('zcmlorder', '50000'))
                        for d, package in [(z2packages, 'zpackage'),
                                           (z2products, 'zproduct')]:
                            if package in oattrs:
                                v = oattrs[package]
                                if not option in d:
                                    d[option] = []
                                if v == 'y':
                                    if not oattrs[package] in d[option]:
                                        d[option].append(oattrs[package])
                                else:
                                    #d[option].append('#%s' % oattrs['name'])
                                    zp = [z.strip()
                                          for z in oattrs[package].split(',')]
                                    noecho = [d[option].append(z)
                                              for z in zp
                                              if not z in d[option]]

        # productdistros handling
        productsdistros = xmlTemplate.getElementsByTagName('productdistros')
        if productsdistros:
            for elem in productsdistros:
                nodes = elem.getElementsByTagName('productdistro')
                for e in nodes:
                    oattrs = dict(e.attributes.items())
                    for option in oattrs['options'].split(','):
                        option = option.strip()
                        if not option in urls_mappings:
                            urls_mappings[option] = []
                        urls_mappings[option].append(oattrs['url'])
    except Exception, e:
        raise
    return result


def read_vars(default_config=None, user_config=None, base_vars=None):
    res = {}
    for config in user_config, default_config:
        if config:
            if os.path.exists(config):
                xml = parseString(open(config).read())
                res = parse_xmlconfig(xml, base_vars)
                break
    return res


# vim:set et sts=4 ts=4 tw=120:
