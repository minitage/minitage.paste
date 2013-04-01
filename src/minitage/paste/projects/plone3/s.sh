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
#
#
#



bin/paster create -t minitage.plone3 p3 inside_minitage=${1:-yes}\
mode=relstorage                             \
with_ploneproduct_fss=y                     \
with_ploneproduct_atbackref=y               \
with_ploneproduct_cachesetup=y              \
with_ploneproduct_collage=y                 \
with_ploneproduct_contentlicensing=y        \
with_ploneproduct_cpwkf=y                   \
with_ploneproduct_csvreplica=y              \
with_ploneproduct_easyshop=y                \
inside_minitage=n                \
with_ploneproduct_flowplayer=y              \
with_ploneproduct_ldap=y                    \
with_ploneproduct_lingua=y                  \
with_ploneproduct_maps=y                    \
with_ploneproduct_plomino=y                 \
with_ploneproduct_plonearticle=y            \
with_ploneproduct_ploneboard=y              \
with_ploneproduct_p4a_cal=y                 \
with_ploneproduct_p4a_vid=y                 \
with_ploneproduct_ploneformgen=y            \
with_ploneproduct_quillsenabled=y           \
with_ploneproduct_quills=y                  \
with_ploneproduct_schematuning=y            \
with_ploneproduct_sgdcg=y                   \
with_ploneproduct_tal_portlet=y             \
with_ploneproduct_truegallery=y             \
with_ploneproduct_vaporisation=y            \
with_ploneproduct_wc_dd_menu=y              \
with_checked_versions=y              \


 # vim:set et sts=4 ts=4 tw=80:
