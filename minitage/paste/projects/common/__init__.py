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

    def __init__(self, name):
        common.Template.__init__(self, name)
        # minitage prefix is sys.exec_prefix
        # there we will add
        # minilays/minilay/minibuild
        # /category/project/
        #    ---
        #    ---
        #    share/
        #         ---
        #         ---
        self.ouput_dir = sys.exec_prefix

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
        deps = [d.strip()\
                for d in vars.get('project_dependencies', '').split(',')]
        eggs = [e.strip()
                for e in vars.get('project_eggs', '').split(',')]

        # get the install path
        path = os.path.join(
            prefix,
            vars['category'],
            vars['project'],
        )

        # set the output dir
        self.output_dir = prefix

        # set templates variables
        vars['eggs'] = eggs
        vars['dependencies'] = deps
        vars['sys'] = self.output_dir
        vars['path'] = path
        vars['mt'] = prefix
        vars['header'] = common.__HEADER__ % {'comment': '#'}

Template.vars = [ common.var('scm_type', 
                       'Repository type (hg|svn|static)', 
                       default = 'hg',),
           common.var('uri', 
                      'Url to checkout', 
                      default = 'http://hg.foo.net',),
           common.var('install_method', 
                      'Install Method', 
                      default = 'buildout',),
           common.var('homepage', 
                      'Homepage', 
                      default = 'http://foo.net',) 
          ]
# vim:set et sts=4 ts=4 tw=80:
