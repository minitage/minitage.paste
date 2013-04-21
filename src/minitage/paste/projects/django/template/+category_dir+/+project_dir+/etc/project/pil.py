import os
import re

ref = re.M|re.I|re.U
def pil(options,buildout):
    cwd = os.getcwd()
    os.chdir(options['compile-directory'])
    ubuntu = False
    try:
        ubuntu = 'ubuntu' in open('/etc/lsb-release').read().lower()
    except Exception, e:
        pass
    libdir = '/usr'
    if ubuntu:
        libdirt = '/usr/lib/x86_64-linux-gnu'
        if os.path.isdir(libdirt):
            libdir = libdirt
    locations = {
        'freetype': buildout.get('freetype', {}).get(
            'location', libdir
        ),
        'jpeg': buildout.get('libjpeg', {}).get (
            'location', libdir
        ),
        'tiff': buildout.get('libtiff', {}).get(
            'location', libdir
        ),
        'zlib': buildout.get('zlib', {}).get(
            'location', libdir
        ),
    }
    st = open('setup.py').read()
    locations['include'] = '/usr/include'
    pregex = [
        ("^(FREETYPE_ROOT.*)$", "FREETYPE_ROOT='%(freetype)s' , '%(include)s'"%locations),
        ("^(TIFF_ROOT.*)$",  "TIFF_ROOT='%(tiff)s', '%(include)s'"%locations),
        ("^(JPEG_ROOT.*)$", "JPEG_ROOT='%(jpeg)s', '%(include)s'"%locations),
        ("^(ZLIB_ROOT.*)$",  "ZLIB_ROOT='%(zlib)s', '%(include)s'"%locations),
    ]

    for p, rep in pregex:
        r= re.compile(p, ref)
        st = r.sub(rep, st)
    open('setup.py', 'w').write(st)
    os.chdir(cwd)
