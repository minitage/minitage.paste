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

import sys
import os
import stat
import getpass
import pwd
import grp

from minitage.paste.profils import common
from minitage.core.common import remove_path
from paste.script import templates

class Template(common.Template):

    summary = 'Template for creating an instance '\
            'of varnish in the sys dir of '\
            'a minitage project.'
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


Template.required_templates = ['minitage.profils.env']
running_user = getpass.getuser()
gid = pwd.getpwnam(running_user)[3]
group = grp.getgrgid(gid)[0]
Template.vars = common.Template.vars + \
        [
            templates.var(
                'vp',
                'Daemon prefix',
                default = os.path.join(sys.prefix, 'dependencies', 'varnish-2.0.3', 'parts', 'part')
            ),
            templates.var('backend', 'Backend', default = 'localhost:8080'),
            templates.var('config', 'You can precise a custom config file to use instead of the default one. The content of this file will be copied into the varnish configuration file (in $sys/etc/varnish).', default = ''),
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

# vim:set et sts=4 ts=4 tw=80:
