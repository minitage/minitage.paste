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
import stat
import getpass
import pwd
import grp

from minitage.paste.instances import common
from paste.script import templates

class Template(common.Template):
    """A Varnish template"""

    summary = 'Template for creating a varnish instance'
    _template_dir = 'template'
    use_cheetah = True

    def post(self, command, output_dir, vars):
        sys = vars['sys']
        dirs = [os.path.join(sys, 'bin'),
                os.path.join(sys, 'etc', 'init.d')]
        for directory in dirs:
            for filep in os.listdir(directory):
                p = os.path.join(directory, filep)
                os.chmod(p, stat.S_IRGRP|stat.S_IXGRP|stat.S_IRWXU)


Template.required_templates = ['minitage.instances.env']
running_user = getpass.getuser()
gid = pwd.getpwnam(running_user)[3]
group = grp.getgrgid(gid)[0]
common_vars = common.Template.vars + [
            templates.var('config', 'You can precise a custom config file '
                          'to use instead of the default one. '
                          'The content of this file will be copied into '
                          'the varnish configuration file (in $sys/etc/varnish).',
                          default = ''),
            templates.var('purge_ips', 'IPs allowed to purge separated by whitespaces', default = 'localhost'),
            templates.var('cache_size', 'Cache size', default = '1G'),
            templates.var('min_ttl', 'Default minimum ttl', default = '3600'),
            templates.var('host_address', 'Host and port to listen on', default = 'localhost:9002'),
            templates.var('telnet_address', 'Telnet interface to listen on', default = 'localhost:9004'),
            templates.var('user', 'Default user', default = running_user),
            templates.var('vhost_vhm', 'Virtualhost name if any', default = 'www.host.tld:80'),
            templates.var('zope_path', 'Site  Path in zope', default = '/plone'),
            templates.var('worker_t', """[int][,int[,int]]
                          # Number of worker threads
                          -w <fixed_count>
                          -w min,max
                          -w min,max,timeout [default: 1,1000,120]""", default="1,1000,120"),
        ]
Template.vars = common_vars +[templates.var('backends',
                                            'Backends separated by whitespaces',
                                            default = 'localhost:8080'),
                              templates.var(
                                  'vp',
                                  'Daemon prefix',
                                  default = os.path.join(sys.prefix, 'dependencies',
                                                         'varnish-1.1.2', 'parts', 'part')
                              ),
                             ]


# vim:set et sts=4 ts=4 tw=80:
