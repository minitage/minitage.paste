# Gopyright (C) 2009, Mathieu PASQUET <kiorky@cryptelium.net>
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

import getpass
import sys
import re
import os

from minitage.core import core
from minitage.paste import common
from paste.script import templates

running_user = getpass.getuser()

class Template(common.Template):
    """A template for minitage.instances"""

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
            m = core.Minimerge({'config': cfg, 'skip_self_upgrade': True})
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
                # reorder dependencies to let the direct dependencies be at most
                # priority
                def sortmb(m1, m2):
                    if m1.name in mb.dependencies:
                        return 1
                    if m2.name in mb.dependencies:
                        return -1
                    return 0
                deps.sort(sortmb)
                vars['dependencies'] = deps

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
        vars['pyver'] = ''
        vars['eggs'] = eggs
        pyname_re = re.compile('python-(\d\.\d)')
        if len(eggs)>0:
            for dep in deps:
                m = pyname_re.match(dep.name)
                if m:
                    vars['pyver'] = m.groups()[0]
                    break
 
        vars['dependencies'] = deps


# vim:set et sts=4 ts=4 tw=80:
