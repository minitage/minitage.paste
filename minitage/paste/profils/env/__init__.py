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

from minitage.paste.profils import common

class Template(common.Template):

    summary = 'Template for creating a file '\
            'to source to get the needed '\
            'environnment variables relative '\
            'to a minitage project.'
    _template_dir = 'template'
    use_cheetah = True

    def __init__(self, name):
        common.Template.__init__(self, name)


# vim:set et sts=4 ts=4 tw=80:
