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

from minitage.paste.projects import common
from minitage.paste.common import var

class Template(common.Template):

    summary = 'Template for creating a '\
            'basic plone31 project inside minitage'


    def pre(self, command, output_dir, vars):
        """register catogory, and roll in common,"""
        vars['category'] = 'zope'
        common.Template.pre(self, command, output_dir, vars)

Template.vars = common.Template.vars \
        + [var('address', 
               'Address to listen on', 
               default = 'localhost',), 
           var('port', 
               'Port to listen to', 
               default = '8080',),  
           var('loglevel', 
               'log level (DEBUG|INFO|WARNING|ERROR)', 
               default = 'INFO',),   
           var('debug', 
               'Debug mode (on|off)', 
               default = 'on',),    
           var('login', 
               'Administrator login', 
               default = 'admin',),     
           var('password', 
               'Password', 
               default = 'admin',),     
          ]
# vim:set et sts=4 ts=4 tw=80:
