#!/usr/bin/env bash

# Copyright (C) 2009, Mathieu PASQUET <mpa@makina-corpus.com>
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

w=$(dirname $0)
cd $w
PY="$w/../../../../../../bin/zopepy"
ver="42"


filter_bad() {
    sed -re  "s/(Paste(Deploy|Script)?\s*=.*)/#\\1 no conflicts !/g" \
        | sed -re "s/extends =/notused-extends =/g"\

}


plone41() {
    plone=$($PY -c "from minitage.paste.projects.plone${ver} import Template as Template;print Template.packaged_version")
    zope2=$($PY -c "from minitage.paste.projects.plone${ver} import Template;print Template.packaged_zope2_version")
    ztk=$($PY -c   "from minitage.paste.projects.plone${ver} import Template;print Template.packaged_ztk_version")
    ver="$(echo $plone | cut -nb1-3)"
    echo
    echo  Refreshing :: $plone / $ver / $zope2 / $ztk
    echo
    if [[ ! -d checkout ]];then
        git clone https://github.com/plone/buildout.coredev.git checkout
    fi
    pushd checkout; git reset --hard; git checkout $ver; git pull; popd
    cat checkout/sources.cfg                                                        | filter_bad > sources.cfg
    wget http://dist.plone.org/release/$plone/versions.cfg                     -O - | filter_bad > versions.cfg
    wget http://download.zope.org/Zope2/index/$zope2/versions.cfg | filter_bad -O - | filter_bad > "zope2.versions.cfg"
    wget http://download.zope.org/zopetoolkit/index/$ztk/ztk-versions.cfg      -O - | filter_bad > "ztk.versions.cfg"
    wget http://download.zope.org/zopetoolkit/index/$ztk/zopeapp-versions.cfg  -O - | filter_bad > "zopeapp.versions.cfg"
    sed -re "/\[versions\]/ {
a #ZTK: $ztkver
}" -i ztk.versions.cfg
}
plone41
# vim:set et sts=4 ts=4 tw=0:
