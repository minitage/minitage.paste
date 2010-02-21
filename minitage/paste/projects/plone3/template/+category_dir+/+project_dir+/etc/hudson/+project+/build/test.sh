#!/usr/bin/env bash
source $(dirname $0)/activate_env.sh
# add packages to be tested here
tested_packages="$tested_packages ${project}.skin"
tested_packages="$tested_packages ${project}.policy"
# run testrunner on each
for i in $tested_packages;do
    $cwd/bin/test -x -m "$i"
done
# copy test reports to workspace as the reporter want relative paths
reportsdir="$WORKSPACE/testhudsonxmlreports"
if [[ -d $reportsdir ]];then
    rm -rf $reportsdir
fi 
mkdir $reportsdir
# $xmlreports come with activate_env
for d in $xmlreports;do
    mkdir "$reportsdir/$d"
    cp -rf "$d/*.xml" "$reportsdir/$d"
done
# vim:set et sts=4 ts=4 tw=80:
