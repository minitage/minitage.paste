# Copyright (C) 2009, Mathieu PASQUET <kiorky@cryptelium.net>
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

import sys
import os


PATH = os.path.join(os.path.dirname(__file__), 'template', 'bin')
MYSQL_PATH = os.environ.get('MMYSQL_PATH',
                         os.path.expanduser('~/minitage/dependencies/mysql-5.1/parts/part/bin')
                          )
MYSQL_PATH2 = os.environ.get('MMYSQL_PATH',
                         os.path.expanduser('~/minitage/dependencies/mysql-5.1/parts/part/libexec')
                          )
WRAPPE_TEMPLATE ="""\
#!/usr/bin/env bash
PATH=$mt/dependencies/mysql-$my_version/libexec:\$PATH
. ${sys}/share/mysql/${db_name}.env
%s $@
"""
opts_progs = {'my_print_defaults': '',
              'mysql': '',
              'mysqlaccess': '',
              'mysqladmin': '',
              'mysqlbinlog': '',
              'mysqlcheck': '',
              'mysql_client_test': '',
              'mysql_client_test_embedded': '',
              'mysql_config': '',
              'mysql_convert_table_format': '',
              'mysqld': '',
              'mysqld_multi': '',
              'mysqld_safe': '',
              'mysqldump': '',
              'mysqldumpslow': '',
              'mysql_find_rows': '',
              'mysql_fix_extensions': '',
              'mysql_fix_privilege_tables': '',
              'mysqlhotcopy': '',
              'mysqlimport': '',
              'mysql_install_db': '',
              'mysqlmanager': '',
              'mysql_secure_installation': '',
              'mysql_setpermission': '',
              'mysqlshow': '',
              'mysqltest': '',
              'mysqltest_embedded': '',
              'mysql_tzinfo_to_sql': '',
              'mysql_upgrade': '',
              'ndb_desc': '',
              'ndb_drop_index': '',
              'ndb_drop_table': '',
              'ndb_error_reporter': '',
              'ndb_mgm': '',
              'ndb_mgmd': '',
              'ndb_print_backup_file': '',
              'ndb_print_schema_file': '',
              'ndb_print_sys_file': '',
              'ndb_restore': '',
              'ndb_select_all': '',
              'ndb_select_count': '',
              'ndb_show_tables': '',
              'ndb_test_platform': '',
              'ndb_waiter': '',
              'perror': '',
              'replace': '',
              'resolveip': '',
              'resolve_stack_dump': '',
             }
def main():
    for p in MYSQL_PATH, MYSQL_PATH2:
        for f in os.listdir(p):
            d = open(os.path.join(PATH, '+db_name+.%s_tmpl' % f), 'w')
            content = WRAPPE_TEMPLATE % (f)
            if f in opts_progs:
                content=content.replace('$@',
                                        '--defaults-file=$sys/etc/mysql/${project}_${db_name}.my.cnf $@')
            d.write(content)
            d.close()

if __name__ == '__main__':
    main()

# vim:set et sts=4 ts=4 tw=80:
