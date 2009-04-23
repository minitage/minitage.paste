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
import re
import subprocess
import sys

from minitage.paste import common
from minitage.core.common import which, search_latest


class Template(common.Template):
    """Common template"""

    def pre(self, command, output_dir, vars):
        common.Template.pre(self, command, output_dir, vars)
        vars['linux'] = 'linux' in sys.platform
        if not 'opt_deps' in vars:
            vars['opt_deps'] = ''
        if vars['inside_minitage']:
            vars['path'] = os.path.join(
                self.output_dir,
                vars['category'],
                vars['project'],
            )
        else:
            vars['category'] = ''
            vars['path'] = self.output_dir

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
                    'Url to checkout (only useful in a minitage)',
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
                    'the Python interpreter to use.',
                    default = sys.executable,)
        ]
# vim:set et sts=4 ts=4 tw=80:
