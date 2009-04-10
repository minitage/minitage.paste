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
import stat
import getpass
import pwd
import grp
import re
import subprocess

from minitage.paste.profils import common
from minitage.core.common import remove_path
from paste.script import templates

re_flags = re.M|re.U|re.I|re.S

class Template(common.Template):

    summary = 'Template for creating init script for paster configs in '\
            'a minitage project.'
    _template_dir = 'template'
    use_cheetah = True

    def pre(self, command, output_dir, vars):
        common.Template.pre(self, command, output_dir, vars)
        config = vars['config']
        if not config.startswith('/'):
            config = os.path.join(vars['path'], config)
        vars['configp'] = os.path.abspath(config)

        if config.endswith('/'):
            config = config[:-1]
        path_elems = config.split('/')[-1].split('.')
        if len(path_elems) > 1:
            vars['config'] = '.'.join(path_elems[:-1])
        else:
            vars['config'] = path_elems[0]

    def post(self, command, output_dir, vars):
        sys = vars['sys']
        dirs = [#os.path.join(sys, 'bin'),
                os.path.join(sys, 'etc', 'init.d')]
        for directory in dirs:
            for filep in os.listdir(directory):
                p = os.path.join(directory, filep)
                os.chmod(p, stat.S_IRGRP|stat.S_IXGRP|stat.S_IRWXU)

Template.required_templates = ['minitage.profils.env']
running_user = getpass.getuser()
gid = pwd.getpwnam(running_user)[3]
group = grp.getgrgid(gid)[0]
Template.vars = common.Template.vars + \
                [
                templates.var('config', 'The configuration file to use as a base for the init script', default = 'prod.ini'),
                templates.var('user', 'Default user', default = running_user),
                templates.var('group', 'Default group', default = group),
                ]



# vim:set et sts=4 ts=4 tw=80:
