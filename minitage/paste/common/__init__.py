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
import sys
import shutil
import re
import logging

from paste.script import templates

from minitage.core import common
from minitage.core import core

re_flags = re.M|re.U|re.I|re.S
SPECIALCHARS = re.compile('[-._@|{(\[|)\]}]', re_flags)

__HEADER__ = """\
%(comment)s!/usr/bin/env bash
%(comment)s
%(comment)s Copyright (C) 2008, Mathieu PASQUET <kiorky@cryptelium.net>
%(comment)s This program is free software; you can redistribute it and/or modify
%(comment)s it under the terms of the GNU General Public License as published by
%(comment)s the Free Software Foundation; either version 2 of the License, or
%(comment)s (at your option) any later version.
%(comment)s This program is distributed in the hope that it will be useful,
%(comment)s but WITHOUT ANY WARRANTY; without even the implied warranty of
%(comment)s MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
%(comment)s GNU General Public License for more details. """

def boolify(d, boolean_values=None):
    if not 'booleans' in d:
        d['booleans'] = []
    if not boolean_values:
        boolean_values = [key
                          for key in d
                          if key.startswith('with_')
                          and (not key in d['booleans'])]
    if not 'inside_minitage' in boolean_values:
            boolean_values.append('inside_minitage')
    d['booleans'].extend(boolean_values)
    for var in boolean_values:
        if var in d:
            if isinstance(d[var], basestring):
                if u'y' in d[var].lower():
                    d[var] = True
                elif u'true' == d[var].lower().strip():
                    d[var] = True
                else:
                    d[var] = False

class Template(templates.Template):

    summary = 'OVERRIDE ME'
    _template_dir = 'template'
    use_cheetah = True
    read_vars_from_templates = True
    special_output_dir = False

    vars = [
        templates.var('project_dependencies',
                      'Dependencies (separated by comma)'),
        templates.var('project_eggs',
                      'minitage packages nn-eggified like libxml2-2.6 '
                      'to be added to the python path '
                      '(separated by comma)'),
        templates.var('inside_minitage',
                      'Are you inside a minitage environment y/n',
                      default='y'),
    ]

    def boolify(self, d, keys=None):
        return boolify(d, keys)

    def __init__(self, name):
        templates.Template.__init__(self, name)
        self.output_dir = os.path.abspath('.')

    def run(self, command, output_dir, vars):
        self.boolify(vars)
        self.pre(command, output_dir, vars)
        # may we have register variables ?
        if self.output_dir:
            if not os.path.exists(self.output_dir):
                os.makedirs(self.output_dir)
            output_dir = self.output_dir
        if not os.path.isdir(output_dir):
            raise Exception('%s is not a directory' % output_dir)
        self.write_files(command, self.output_dir, vars)
        self.post(command, output_dir, vars)

    def check_vars(self, vars, cmd):
        """add mandatory check"""
        cvars = templates.Template.check_vars(self, vars, cmd)
        for var in cvars:
            for mvar in self.vars:
                if mvar.name == var:
                    if getattr(mvar, 'mandatory', False)\
                       and not cvars[var]:
                        raise Exception('%s must be set' % var)

        return cvars

    def read_vars(self, command=None):
        python = '%s' % (
            '\tMinitage will try to use a python from its built dependencies if you\n'
            '\tare in a minitage environment. In other words, il will add it to your minibuild.\n'
            '\tIf you are not inside a minitage,  it will try to find one installed on your system ($PATH).\n'
        )
        if getattr(self, 'python', None):
            python +='\tThe selected paster indicate that you must use %s.\n' % self.python
        if command:
            if not command.options.quiet:
                print "%s" % (
                    '---------------------------------------------------------\n'
                    '\tMinitage support is now optionnal.\n'
                    '\tWarning: All minitage templates come by default '
                    'with their dependencies (including xml parsing and databases). You ll not have to '
                    'specify them.\n'
                    '\tMany of the variables are optionnal or have good defaults provided.\n'
                    '\tJust press enter to continue the process.\n'
                    '%s'
                    '---------------------------------------------------------\n'
                ) % python
        self.lastlogs=[]
        return templates.Template.read_vars(self, command)

    def pre(self, command, output_dir, vars):
        self.boolify(vars)
        vars['booleans'] = []
        self.special_output_dir = not(command.options.output_dir.strip() in ['', '.'])
        # either / or virtualenv prefix is the root
        # of minitage in any cases.
        # This is pointed out by sys.exec_prefix, hopefullly.
        vars['booleans'].append('inside_minitage')
        prefix = os.path.join(command.options.output_dir)
        if vars['inside_minitage'] and not self.special_output_dir:
            prefix = sys.exec_prefix
        if not vars['inside_minitage'] and not self.special_output_dir:
            prefix = os.path.join(command.options.output_dir, vars['project'])
        self.old_output_dir = getattr(self, 'output_dir', None)
        self.output_dir = prefix
        # find the project minibuild
        deps = [d.strip()\
                for d in vars.get('project_dependencies', '').split(',')]
        eggs = [e.strip()
                for e in vars.get('project_eggs', '').split(',')]
        # set templates variables
        vars['header'] = __HEADER__ % {'comment': '#'}
        vars['eggs'] = eggs
        vars['dependencies'] = deps
        vars['minilay'] = vars['project']
        if vars['inside_minitage']:
            not_minitage = False
            vars['mt'] = self.output_dir
            if self.special_output_dir:
                vars['path'] = self.output_dir
            # call to be in minitage but deport
            # the minitage ROOT to the 'MT' environment variable
            # this variable is set automaticly by the minitage.instances.env
            # template which must has been used to set the current environment
            if not (os.path.exists(
                os.path.join(vars['mt'], 'etc', 'minimerge.cfg')
            )) and 'MT' in os.environ: 
                if os.path.exists(
                    os.path.join(os.environ['MT'], 'etc', 'minimerge.cfg')
                ):
                    vars['mt'] = os.environ['MT']  
        else:
            not_minitage = True
        if not_minitage or not (os.path.exists(
            os.path.join(vars['mt'], 'etc', 'minimerge.cfg')
        )):
            if not self.special_output_dir:
                vars['inside_minitage'] = False
            vars['mt'] = sys.prefix
        vars['mt_fp'] = vars['mt']

    def post(self, command, output_dir, vars):
        paths = []
        minilays = os.path.join(self.output_dir, 'minilays')
        if not vars['inside_minitage']:
            if os.path.isdir(minilays):
                if 2 > len(os.listdir(minilays)):
                    paths.append(minilays)
            for p in paths:
                fp = os.path.join(self.output_dir, p)
                if os.path.exists(fp):
                    shutil.rmtree(fp)

        if self.lastlogs and not command.options.quiet:
            print
            print
            print
            print 'PASTER MESSAGES'
            print
            for log in self.lastlogs:
                print log

class var(templates.var):
    """patch pastescript to have mandatory fields"""

    def __init__(self, name, description,
                 default='', should_echo=True,
                mandatory = False):
        templates.var.__init__(self, name, description,
                                default, should_echo)
        self.mandatory = mandatory

# vim:set et sts=4 ts=4 tw=80:
