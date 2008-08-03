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

import os
import sys

from minitage.core import core
from minitage.paste import common

class Template(common.Template):

    def pre(self, command, output_dir, vars):

        name = vars['project']

        # either / or virtualenv prefix is the root
        # of minitage in any cases.
        # This is pointed out by sys.exec_prefix, hopefullly.
        prefix = sys.exec_prefix
        cfg = os.path.join(prefix, 'etc', 'minimerge.cfg')

        # load the minimerge
        m = core.Minimerge({'config': cfg})

        # find the project minibuild
        mb = m.find_minibuild(name)
        adeps = m.compute_dependencies([name])
        deps = [lmb for lmb in adeps if lmb.category == 'dependencies']
        eggs = [lmb for lmb in adeps if lmb.category == 'eggs']

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

        # get the install path
        path = m.get_install_path(mb)

        # set the output dir
        self.output_dir = os.path.join(path, 'sys')

        # set templates variables
        vars['eggs'] = eggs
        vars['sys'] = self.output_dir
        vars['path'] = path
        vars['category'] = mb.category
        vars['mt'] = prefix
        vars['dependencies'] = deps
        vars['header'] = common.__HEADER__ % {'comment': '#'}

# vim:set et sts=4 ts=4 tw=80:
