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
import re
import subprocess
import pkg_resources

from minitage.paste import common
from minitage.core.common import which, search_latest

class Template(common.Template):
    """Common template"""

    def post(self, command, output_dir, vars):
        self.lastlogs.append(
            '* A project has been created in %s.\n' % vars['path']
        )
        minilay = os.path.join(self.output_dir, 'minilays', vars['project'])
        if vars['inside_minitage']:
            self.lastlogs.append(
                '* A minilay has been installed in %s.\n'
                '* It contains those minilbuilds:'
                '\n\t- %s \n'
                '\n'
                '* Think to finish the versionning stuff and put this minilay and'
                ' the projet under revision control.\n'
                '* The project must be archived here \'%s\' using \'%s\' or change the minibuild '
                'src_uri/scm_type.\n'
                '* Install your project running: \n\t\tminimerge -v %s'
                ''% (
                    minilay,
                    '\n\t- '.join(os.listdir(minilay)),
                    vars['uri'], vars['scm_type'],
                    vars['project']
                )
            )
        self.lastlogs.append(
            '* You can additionnaly create related databases or configuration or'
            ' other stuff using minitage instances '
            ' (http://minitage.org/paster/instances/index.html)\n'
            '* Available instances are: \n'
            '\t- %s\n'
            '* Some extra instances are contained inside the'
            '\'minitage.paste.extras package\', install it as a classical egg.\n'
            '* Run an instance with: \n'
            ' \tpaster create -t minitage.instances.PROFIL project\n'
            '\n' % (
                '\n\t- '.join(
                    ["%s (%s)" % (
                        a,
                        pkg_resources.load_entry_point('minitage.paste',
                                         'paste.paster_create_template',
                                         a
                                        ).summary
                    )
                        for a in pkg_resources.get_entry_map(
                            'minitage.paste'
                        )['paste.paster_create_template']
                        if 'minitage.instances' in a]
                )
            )

        )
        README = os.path.join(vars['path'],'README.%s.txt' % vars['project'])
        open(README, 'w').write('\n'.join(self.lastlogs))
        self.lastlogs.append(
            'Those informations have been writed to %s.' % README
        )
        return common.Template.post(self, command, output_dir, vars)

    def pre(self, command, output_dir, vars):
        common.Template.pre(self, command, output_dir, vars)
        vars['linux'] = 'linux' in sys.platform
        if not 'opt_deps' in vars:
            vars['opt_deps'] = ''
        if vars['inside_minitage']:
            if not self.special_output_dir:
                vars['path'] = os.path.join(
                    self.output_dir,
                    vars['category'],
                    vars['project'],
                )
            else:
                vars['path'] = self.output_dir
        else:
            vars['category'] = ''
            vars['path'] = self.output_dir
        if not self.special_output_dir:
            vars['project_dir'] = vars['project']
            vars['categoy_dir'] = vars['category']
        else:
             vars['project_dir'] = ''
             vars['category_dir'] = ''
        xml2, xslt ='py-libxml2-2.6', 'py-libxslt-1.1'
        interpreter, pyver = None, None
        pythons = {
            'python2.4': '2.4',
            'python2.5': '2.5',
            'python2.6': '2.6',
            'python3.0': '3.0',
            'python3.1': '3.1',
            'python3.2': '3.2',
        }
        python = getattr(self, 'python', None)
        if vars['inside_minitage']:
            latest_python = None
            dsearch_latest = {'py-libxslt.*': 'xslt',
                             'py-libxml2.*': 'xml2',
                             'python-\d.\d': 'latest_python'}
            vars['minilays'] = minilays = os.path.join(vars['mt'], 'minilays')
            for regex in dsearch_latest.keys():
                minibuild = search_latest(regex, minilays)
                stmt = '%s=\'%s\'' % (dsearch_latest[regex], minibuild)
                exec  stmt
                del dsearch_latest[regex]
            if (not python) and latest_python:
                python = latest_python
            pyver = pythons[python.replace('-', '')]
        else:
            if not python:
                python = vars['python']
            else:
                python = python.replace('-', '')
                pyver = pythons[python]
            interpreter = which(python)
            executable_version = os.popen(
                '%s -c "%s"' % (
                    interpreter,
                    'import sys;print sys.version[:3]'
                )
            ).read().replace('\n', '')
            executable_prefix = os.path.abspath(
                subprocess.Popen(
                    [interpreter, '-c', 'import sys;print sys.prefix'],
                    stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                    close_fds=True).stdout.read().replace('\n', '')
            )
            if pyver and (executable_version != pyver):
                try:
                    interpreter = which('python%s' % pyver)
                    executable_version = os.popen(
                        '%s -c "%s"' % (
                            interpreter,
                            'import sys;print sys.version[:3]'
                        )
                    ).read().replace('\n', '')
                    executable_prefix = os.path.abspath(
                        subprocess.Popen(
                            [interpreter, '-c', 'import sys;print sys.prefix'],
                            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                            close_fds=True).stdout.read().replace('\n', '')
                    )
                except:
                    print 'Cant find a python %s installation, you didnt give a %s python to paster' % (pyver, pyver)
                    raise
            if pyver and (executable_version != pyver):
                print 'Cant find a python %s installation, you didnt give a %s python to paster' % (pyver, pyver)
                raise Exception('Incompatible python')

        if vars['inside_minitage']:
            interpreter = os.path.join(
                '${buildout:directory}', '..', '..',
                'dependencies', python, 'parts', 'part', 'bin', 'python')
            executable_prefix = os.path.join(
                vars['mt'], 'dependencies',
                'python-%s' %  pyver, 'parts', 'part')
            executable_version = pyver
            vars['opt_deps'] = '%s %s  %s' % (xml2, xslt, 'python-%s' %  pyver)
            vars['xml2'] = os.path.join('${minitage:location}',
                                        'eggs', xml2,
                                    'parts', 'site-packages-%s' % pyver)
            vars['xslt'] = os.path.join('${minitage:location}',
                                    'eggs', xslt,
                                    'parts', 'site-packages-%s' % pyver)
            vars['mt'] = '${buildout:directory}/../..'
        else:
            vars['xml2'] = os.path.join(executable_prefix, 'lib', 'python%s' % executable_version, 'site-packages')
            vars['xslt'] = os.path.join(executable_prefix, 'lib', 'python%s' % executable_version, 'site-packages')
            vars['opt_deps'] = ''

        # minitage needs python.
        if not interpreter and (not vars['inside_minitage']):
            raise Exception('Python interpreter not found')

        vars['python'] = interpreter
        vars['python_minibuild'] = 'python-%s' % pyver
        vars['python_version'] = executable_version
        vars['executable_site_packages'] = os.path.join(
            executable_prefix, 'lib', 'python%s'%executable_version, 'site-packages')
        vars['executable_prefix'] = executable_prefix

Template.vars = common.Template.vars + \
        [\
         common.var('scm_type',
                    'Minibuild checkout facility'
                    ' (git|bzr|hg|svn|static)\n'
                    'static can be used for both '
                    'http, ftp and file:// uris: '
                    '(only useful in a minitage)',
                    default = 'hg',),
         common.var('uri',
                    'Url of the project to checkout (only useful in a minitage)',
                    default = 'http://hg.foo.net',),
         common.var('install_method',
                    'The install method of your minibuild '
                    '(only useful in a minitage)',
                    default = 'buildout',),
         common.var('homepage',
                    'Homepage url of your project '
                    '(only useful in a minitage)',
                    default = 'http://foo.net',),
         common.var('python',
                    'the Python interpreter to use. (Only useful if you are not'
                    'inside a minitage.',
                    default = sys.executable,)
        ]
# vim:set et sts=4 ts=4 tw=80:
