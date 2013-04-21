#!/usr/bin/env python
# WARNING
# GENERATED AND OVERWRITTEN BY BUILDOUT
#
# -*- coding: utf-8 -*-
__docformat__ = 'restructuredtext en'
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '${buildout:directory}/var/db.sqlite3',
    }
    #'default': {
    #    'ENGINE': 'django.db.backends.mysql',
    #    'OPTIONS':{
    #        'db': '${settings:mysql_database}',
    #        'host': '${hosts:mysql}',
    #        'port': int('${ports:mysql}'),
    #        'user': '${users:django}',
    #        'passwd': '${passwords:mysql}',
    #    }
    #}
}
WEBSITE_URL='http://${reverse_proxy:host}'
DEBUG = '${settings:debug}'.lower().strip() == 'true'
TIME_ZONE = 'Europe/Paris'
LANGUAGE_CODE = 'fr-fr'
MEDIA_URL = WEBSITE_URL+'/media/'
ADMINS = (
     ('admin', '${settings:adminmail}'),
)

BROKER_URL='amqp://${users:django}:${passwords:rabbitmq}@${hosts:rabbitmq}:${ports:rabbitmq}'
DEFAULT_FROM_EMAIL='${settings:adminmail}'

GOOGLE_STEP2_URI = WEBSITE_URL + '/gwelcome'
GOOGLE_CLIENT_ID = '${settings:google_client_id}'
GOOGLE_CLIENT_SECRET = '${settings:google_client_secret}'
#from pymongo import Connection
#MONGO_CONNECTION = Connection(
#    safe=True, j=True,
#    host='${hosts:mongodb}', port=int('${ports:mongodb}'))
# vim:set et sts=4 ts=4 tw=80:
