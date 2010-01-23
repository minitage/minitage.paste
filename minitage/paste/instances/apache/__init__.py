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
import getpass
import stat

from paste.script import templates
from minitage.paste.instances import common
running_user = getpass.getuser()

class Template(common.Template):
    """A apache template"""
    summary = 'Template for creating an apache instance'
    def pre(self, command, output_dir, vars):
        common.Template.pre(self, command, output_dir, vars) 
        sys = vars['sys']
        vars['dr'] = os.path.join(sys, 'var', 'www', vars['project'])
        vars['mdr'] = os.path.join(sys, 'var', 'www', vars['project'], 'htdocs')
        vars['logs'] = os.path.join(sys, 'var', 'log', 'apache', vars['project'] )
        vars['ssl'] = os.path.join(sys, 'etc', 'ssl', 'apache')
        vars['conf'] = os.path.join(sys, 'etc', 'apache', vars['project'] )


    def post(self, command, output_dir, vars):
        sys = vars['sys']
        dirs = [os.path.join(sys, 'bin'),
                os.path.join(sys, 'etc', 'init.d')]
        for directory in dirs:
            for filep in os.listdir(directory):
                p = os.path.join(directory, filep)
                os.chmod(p, stat.S_IRGRP|stat.S_IXGRP|stat.S_IRWXU)
        common.Template.post(self, command, output_dir, vars)

Template.vars = common.Template.vars + \
        [templates.var('http_address',  'HTTP address to listen on', default =
                       '0.0.0.0'),
         templates.var('http_port',  'HTTP  port to listen on', default = '9080'),
         templates.var('https_address', 'HTTPS address to listen on', default =
                       '0.0.0.0'),
         templates.var('https_port', 'HTTPS port to listen on', default = '9443'),
         templates.var('server_name', 'Default servername', default = 'localhost'),
         templates.var('user', 'Default user', default = running_user),
        ]

# vim:set et sts=4 ts=4 tw=80:
