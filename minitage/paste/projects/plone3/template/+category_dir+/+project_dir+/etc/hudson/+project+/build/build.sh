#!/usr/bin/env bash
source $(dirname $0)/activate_env.sh
# build all dependencies if not already installed
minimerge  -v --only-dependencies  $project
if [[ $? != 0 ]];then exit $?;fi
minimerge  -NRuv $project
if [[ $? != 0 ]];then exit $?;fi 
# vim:set et sts=4 ts=4 tw=80:
