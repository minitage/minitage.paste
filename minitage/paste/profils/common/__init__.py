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

from minitage.paste import common
import sys
import os

from minitage.core import core

class Template(common.Template):
    '''A template for minitage profils/'''

    def pre(self, command, output_dir, vars):
        common.Template.pre(self, command, output_dir, vars)
        m = None
        eggs, deps = [], []
        path = self.output_dir
        if vars['inside_minitage']:
            # either / or virtualenv prefix is the root
            # of minitage in any cases.
            # This is pointed out by sys.exec_prefix, hopefullly.
            prefix = sys.exec_prefix
            cfg = os.path.join(prefix, 'etc', 'minimerge.cfg')
            # load the minimerge
            m = core.Minimerge({'config': cfg})
            # find the project minibuild
            try:
                mb = m.find_minibuild(vars['project'])
            except Exception , e:
                vars['inside_minitage'] = False
            else:
                adeps = m.compute_dependencies([vars['project']])
                deps = [lmb for lmb in adeps if lmb.category == 'dependencies']
                eggs = [lmb for lmb in adeps if lmb.category == 'eggs']
                vars['category'] = mb.category
                vars['path'] = m.get_install_path(mb) 
                vars['sys'] = os.path.join(vars['path'], 'sys')

        if not vars['inside_minitage']:
            self.output_dir = os.path.join(os.getcwd(), vars['project'])
            vars['category'] = ''
            vars['path'] = self.output_dir
            vars['sys'] = self.output_dir

        self.output_dir = vars['sys']
        mdeps =  vars.get('project_dependencies', '').split(',')
        for d in mdeps:
            if d:
                manual_dep = m.find_minibuild(d.strip())
                if not manual_dep in deps:
                    deps.append(manual_dep)

        meggs =  vars.get('project_eggs', '').split(',')
        for d in meggs:
            if d:
                manual_egg = m.find_minibuild(d.strip())
                if not manual_egg in eggs:
                    eggs.append(manual_egg)

        # set templates variables
        vars['eggs'] = eggs
        vars['dependencies'] = deps

# vim:set et sts=4 ts=4 tw=80:
