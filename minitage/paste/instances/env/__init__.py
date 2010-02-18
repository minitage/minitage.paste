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
import re
from minitage.paste.instances import common

reflags = re.M|re.S|re.U

class Template(common.Template):

    summary = 'Template for creating a file '\
            'to source to get the needed '\
            'environment variables for '\
            'playing in the shell or for other templates'
    _template_dir = 'template'
    use_cheetah = True

    def pre(self, command, output_dir, vars):
        common.Template.pre(self, command, output_dir, vars)
        vars['ENVVAR'] = 'MINITAGE%s' % (
            re.sub(
                '[.-_*,@#]', '',
                vars['project'], reflags
            )
        )

    def post(self, command, output_dir, vars):
        common.Template.post(self, command, output_dir, vars)
        p = os.path.join(
            vars['sys'], 'share','minitage'
        )
        for l in os.listdir(p):
            fp = os.path.join(p, l)
            os.chmod(fp, 0755)


# vim:set et sts=4 ts=4 tw=80:
