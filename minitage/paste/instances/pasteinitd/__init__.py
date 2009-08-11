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
import stat
import getpass
import pwd
import grp
import re
import subprocess

from minitage.paste.instances import common
from minitage.core.common import remove_path
from paste.script import templates

re_flags = re.M|re.U|re.I|re.S

class Template(common.Template):

    summary = 'Template for creating init script for paster serve'
    _template_dir = 'template'
    use_cheetah = True

    def pre(self, command, output_dir, vars):
        common.Template.pre(self, command, output_dir, vars)
        config = vars['config']
        if not config.startswith('/'):
            if vars['inside_minitage']:
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
        dirs = [os.path.join(sys, 'etc', 'init.d')]
        for directory in dirs:
            for filep in os.listdir(directory):
                p = os.path.join(directory, filep)
                os.chmod(p, stat.S_IRGRP|stat.S_IXGRP|stat.S_IRWXU)

Template.required_templates = ['minitage.instances.env']
running_user = getpass.getuser()
gid = pwd.getpwnam(running_user)[3]
group = grp.getgrgid(gid)[0]
Template.vars = common.Template.vars + \
                [
                templates.var('config', 'The configuration file to use as a base for the init script', default = 'prod.ini'),
                templates.var('with_reload', 'Enable auto reloading of the'
                              'server on code changes. [y/n]', default= 'n'),
                templates.var('user', 'Default user', default = running_user),
                templates.var('group', 'Default group', default = group),
                ]



# vim:set et sts=4 ts=4 tw=80:
