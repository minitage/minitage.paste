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


PATH = os.path.join(os.path.dirname(__file__), 'template', 'bin')
LDAP_PATH = os.environ.get('MLDAP_PATH',
                         os.path.expanduser('~/minitage/dependencies/openldap-2.4/parts/part/bin')
                          )
LDAP_PATHS = os.environ.get('MLDAP_PATHS',
                         os.path.expanduser('~/minitage/dependencies/openldap-2.4/parts/part/sbin')
                        )
LDAP_PATHL = os.environ.get('MLDAP_PATHL',
                         os.path.expanduser('~/minitage/dependencies/openldap-2.4/parts/part/libexec')
                        )
WRAPPER_TEMPLATE ="""\
#!/usr/bin/env bash
. ${sys}/share/openldap/${project}_${db_orga}.${db_suffix}.env
# do not borrow LD LINKS from minitage as we can have more than one db in
# environment and it can fuck up OpenLDAP binaries !
unset LD_LIBRARY_PATH
for a in \$@;do
    if [[ \$a == -w* ]];then
        passwordsupplied=True
    fi
    ARGS="\$ARGS \$a"
done
if [[ -z \$passwordsupplied ]];then
    ARGS=" \$ARGS -W"
fi
ARGS=" \$ARGS -x "
%s \$ARGS
"""

SLAP_WRAPPER_TEMPLATE ="""\
#!/usr/bin/env bash
. ${sys}/share/openldap/${project}_${db_orga}.${db_suffix}.env
# do not borrow LD LINKS from minitage as we can have more than one db in
# environment and it can fuck up OpenLDAP binaries !
unset LD_LIBRARY_PATH
%s -f '$slapdconf' \$@
"""

def main():
    for p in LDAP_PATH, LDAP_PATHS, LDAP_PATHL:
        for f in os.listdir(p):
            template = WRAPPER_TEMPLATE
            if f.startswith('slap'):
                template = SLAP_WRAPPER_TEMPLATE
            d = open(os.path.join(PATH, '+db_orga+.+db_suffix+.%s_tmpl' % f), 'w')
            d.write(template % (f))
            d.close()

if __name__ == '__main__':
    main()


# vim:set et sts=4 ts=4 tw=80:
