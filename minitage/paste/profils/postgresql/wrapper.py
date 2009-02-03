#!/usr/bin/env python

# Copyright (C) 2009, Mathieu PASQUET <kiorky@cryptelium.net>
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


PATH = os.path.join(os.path.dirname(__file__), 'template', 'bin')
PG_PATH = os.environ.get('MPG_PATH',
                         os.path.expanduser('~/minitage/mt/dependencies/postgresql-8.3/parts/part/bin')
                        )
WRAPPE_TEMPLATE ="""\
#!/usr/bin/env bash
source ${sys}/share/postgresql/${db_name}.env
%s $@
"""



def main():
    for f in os.listdir(PG_PATH):
        d = open(os.path.join(PATH, '+db_name+.%s_tmpl' % f), 'w')
        d.write(WRAPPE_TEMPLATE % f)
        d.close()


if __name__ == '__main__':
    main()


# vim:set et sts=4 ts=4 tw=80:
