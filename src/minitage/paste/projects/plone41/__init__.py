# Copyright (C) 2009, Makina Corpus <freesoftware@makina-corpus.com>
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

import pkg_resources

from minitage.paste.projects import (
    common, plone4, plone3)

default_config = pkg_resources.resource_filename(
    'minitage.paste',
    'projects/plone41/minitage.plone41.xml')
user_config = os.path.join(os.path.expanduser('~'), '.minitage.plone41.xml')
xmlvars = common.read_vars(default_config, user_config, plone4.xmlvars)
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
checked_versions_mappings = xmlvars.get('checked_versions_mappings', {})
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
        common.var(
            'with_autocheckout_%s' % name,
            description=name,
            default="n",
        )
    )


class Template(plone4.Template):
    packaged_version = '4.1.6'
    #packaged_zope2_version = '2.13.13'
    #packaged_ztk_version = '1.0.6'
    summary = 'Template for creating a plone41 project'
    _template_dir = pkg_resources.resource_filename(
        'minitage.paste', 'projects/plone3/template')
    python = 'python-2.6'
    #default_template_package   = 'ZopeSkel'
    #default_template_epn       = 'paste.paster_create_template'
    #default_template_templaten = 'plone3_buildout'
    init_messages = tuple()
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
        vars = plone4.Template.read_vars(self, command)
        return vars

    def pre(self, command, output_dir, vars):
        """register catogory, and roll in common,"""
        return plone4.Template.pre(self, command, output_dir, vars)

    def post_default_template_hook(self, command, output_dir, vars, ep):
        pass

Template.vars = common.Template.vars + [
    common.var('plone_version',
               'Plone version, default is the one supported and packaged',
               default=Template.packaged_version,),
    common.var('zope2_version',
               'Zope2 version, default is the one supported and packaged',
               default=Template.packaged_zope2_version,),
] + plone3.plone_vars + Template.addons_vars + dev_vars
# vim:set et sts=4 ts=4 tw=0:
