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
import os
def egg(o, b):
    """patch egg version
    you can put a patches/version-${project:django-version}.diff
    to override default .diff"""
    patch_dir = os.path.join( b['buildout']['directory'], 'patches')
    patch_file = os.path.join(patch_dir, 'version.diff')
    patch = 'version-%s.diff ' % b['project']['django-version'] 
    if os.path.exists(patch):
        patch_file = patch
    os.system("""
              cd %s;      
              %s %s<%s""" % (
                  o['compile-directory'],
                  o.get('patch-binary', 'patch'),
                  o.get('patch-options', '-p0'),
                  patch_file
              )
             )

# vim:set et sts=4 ts=4 tw=80:
