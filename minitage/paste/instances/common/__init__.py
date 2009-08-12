# Gopyright (C) 2009, Mathieu PASQUET <kiorky@cryptelium.net>
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

import getpass
import sys
import os

from minitage.core import core
from minitage.paste import common
from paste.script import templates

from OpenSSL.crypto import TYPE_RSA, TYPE_DSA, Error, PKey, PKeyType
from OpenSSL.crypto import X509, X509Type, X509Name, X509NameType
from OpenSSL.crypto import X509Req, X509ReqType
from OpenSSL.crypto import X509Extension, X509ExtensionType
from OpenSSL.crypto import load_certificate, load_privatekey
from OpenSSL.crypto import FILETYPE_PEM, FILETYPE_ASN1, FILETYPE_TEXT
from OpenSSL.crypto import dump_certificate, load_certificate_request
from OpenSSL.crypto import dump_certificate_request, dump_privatekey

running_user = getpass.getuser()

class Template(common.Template):
    '''A template for minitage.instances/'''

    def pre(self, command, output_dir, vars):
        common.Template.pre(self, command, output_dir, vars)
        m = None
        eggs, deps = [], []
        path = self.output_dir
        if vars['inside_minitage']:
            # either / or virtualenv prefix is the root
            # of minitage in any cases.
            # This is pointed out by sys.exec_prefix, hopefullly.
            prefix = sys.exec_prefix
            cfg = os.path.join(prefix, 'etc', 'minimerge.cfg')
            # load the minimerge
            m = core.Minimerge({'config': cfg})
            # find the project minibuild
            try:
                mb = m.find_minibuild(vars['project'])
            except Exception , e:
                vars['inside_minitage'] = False
            else:
                adeps = m.compute_dependencies([vars['project']])
                deps = [lmb for lmb in adeps if lmb.category == 'dependencies']
                eggs = [lmb for lmb in adeps if lmb.category == 'eggs']
                vars['category'] = mb.category
                vars['path'] = m.get_install_path(mb)
                vars['sys'] = os.path.join(vars['path'], 'sys')

        if not vars['inside_minitage']:
            self.output_dir = os.path.join(os.getcwd(), vars['project'])
            vars['category'] = ''
            vars['path'] = self.output_dir
            vars['sys'] = self.output_dir

        self.output_dir = vars['sys']
        mdeps =  vars.get('project_dependencies', '').split(',')
        for d in mdeps:
            if d:
                manual_dep = m.find_minibuild(d.strip())
                if not manual_dep in deps:
                    deps.append(manual_dep)

        meggs =  vars.get('project_eggs', '').split(',')
        for d in meggs:
            if d:
                manual_egg = m.find_minibuild(d.strip())
                if not manual_egg in eggs:
                    eggs.append(manual_egg)

        # set templates variables
        vars['eggs'] = eggs
        vars['dependencies'] = deps


def dump_write(content, dump_path):
    f = open(dump_path, 'w')
    f.write(content)
    f.close()

def set_x509(kw, xname = None):
    if not xname:
        # XXX There's no other way to get a new X509Name yet.
        xname = X509().get_subject()

    xname.countryName = kw['C']
    xname.stateOrProvinceName = kw['ST']
    xname.localityName = kw['L']
    xname.organizationName = kw['O']
    xname.organizationalUnitName = kw['OU']
    xname.emailAddress = kw['emailAddress']
    xname.commonName = kw['CN']

    return xname

def set_x509_serv(xname=None, vars = None):
    kw = {
         'C':'FR',
         'ST':'StateServ',
         'L':'NantesServ',
         'O':'OrgServ',
         'OU':'UnitServ',
         'emailAddress':'dj.coin@laposte.net',
         }
    kw['CN'] = vars.get('host', 'servcas')
    for var in kw:
        key = 'ssl_server_%s' % var
        if key in vars:
            kw[var] = vars[key]
    return set_x509(kw, xname)

def set_x509_ca(xname=None, vars = None):
    kw = {
        'C':'FR',
        'ST':'StateCA',
        'L':'TownCa',
        'O':'OrgCA',
        'OU':'UnitCA',
        'emailAddress':'foo@foo.com',
    }
    kw['CN'] = vars.get('host', 'localhost')
    for var in kw:
        key = 'ssl_ca_%s' % var
        if key in vars:
            kw[var] = vars[key]
    return set_x509(kw, xname)

def generate_prefixed_ssl_bundle(vars, name):
    spath = os.path.join(vars['sys'], 'etc' , 'ssl')
    make_certificate(
        os.path.join(spath, 'certs', '%s-ca.crt' % (name)),
        os.path.join(spath, 'private', '%s-ca.key' % (name)),
        os.path.join(spath, 'certs', '%s-server.crt' % (name)),
        os.path.join(spath, 'private', '%s-server.key' % (name)),
        vars=vars
    )

def make_certificate(
    ca_crt_path = 'ca.crt',
    ca_key_path = 'ca.key',
    server_crt_path = 'server.crt',
    server_key_path  = 'server.key',
    vars=None):

    # make the certificat of CA
    # need passphrase ?
    ca_key = PKey()
    ca_key.generate_key(TYPE_RSA, 1024)
    dump_write(dump_privatekey(FILETYPE_PEM, ca_key),
               ca_key_path)

    # MAKE THE CA SELF-SIGNED CERTIFICATE
    cert =  X509()
    sub = cert.get_subject()
    set_x509_ca(sub, vars=vars)

    #FORMAT : YYYYMMDDhhmmssZ
    after =  '20200101000000Z'
    before = '20090101000000Z'
    cert.set_notAfter(after)
    cert.set_notBefore(before)

    cert.set_serial_number(1)
    cert.set_pubkey(ca_key)
    cert.set_issuer(cert.get_subject())

    cert.sign(ca_key,"MD5")
    dump_write(dump_certificate(FILETYPE_PEM, cert),
               ca_crt_path)
    print "Generated CA certificate in %s" % ca_crt_path

    # MAKE THE SERVER CERTIFICATE
    s_key = PKey()
    s_key.generate_key(TYPE_RSA, 1024)
    dump_write(dump_privatekey(FILETYPE_PEM, s_key),
               server_key_path)
    s_cert = X509()
    s_sub = s_cert.get_subject()
    set_x509_serv(s_sub, vars=vars)

    #FORMAT : YYYYMMDDhhmmssZ
    after =  '20200101000000Z'
    before = '20090101000000Z'
    s_cert.set_notAfter(after)
    s_cert.set_notBefore(before)

    s_cert.set_serial_number(2)
    s_cert.set_pubkey(s_key)
    s_cert.set_issuer(cert.get_subject())

    s_cert.sign(ca_key,"MD5")
    dump_write(dump_certificate(FILETYPE_PEM, s_cert),
               server_crt_path)
    print "Generated Server certificate in %s" % server_crt_path
    for p in [ca_key_path, server_key_path]:
        os.chmod(p, 0600)

SSL_VARS = [
    templates.var('ssl_ca_C', 'SSL Ca Country', default = 'FR'),
    templates.var('ssl_ca_L', 'SSL Ca town', default = 'Paris'),
    templates.var('ssl_ca_ST', 'SSL Ca state', default = 'CaState'),
    templates.var('ssl_ca_O', 'SSL Ca Organization', default = 'organizationCorp'),
    templates.var('ssl_ca_OU', 'SSL Ca Unit', default = 'SpecialUnit'),
    templates.var('ssl_ca_emailAddress', 'SSL Ca email', default = '%s@localhost'%running_user),
    templates.var('ssl_server_C', 'SSL Server Country', default = 'FR'),
    templates.var('ssl_server_L', 'SSL Server town', default = 'Paris'),
    templates.var('ssl_server_ST', 'SSL Server state', default = 'ServerState'),
    templates.var('ssl_server_O', 'SSL Server Organization', default = 'organizationCorp'),
    templates.var('ssl_server_OU', 'SSL Server Unit', default = 'SpecialUnit'),
    templates.var('ssl_server_emailAddress', 'SSL Server email',
                  default = '%s@localhost' % ( running_user)
                 ),
]
# vim:set et sts=4 ts=4 tw=80:
