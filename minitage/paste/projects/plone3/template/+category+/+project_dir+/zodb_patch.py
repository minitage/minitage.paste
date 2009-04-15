# relstorage patch for ZODB
import os

curdir = os.path.realpath(os.path.dirname(__file__))

PATCH_NAME = 'poll-invalidation-1-zodb-3-7-1.patch'
ZODB_FOLDER = os.path.join(curdir, 'parts', 'zope2', 'lib', 'python', 'ZODB')

patch_content = open(os.path.join(curdir, 'patches', PATCH_NAME)).read()

copy = os.path.join(ZODB_FOLDER, PATCH_NAME)
f = open(copy, 'w')
try:
    f.write(patch_content)
finally:
    f.close()

os.chdir(ZODB_FOLDER)
os.system('patch -p1 < %s' % PATCH_NAME)


