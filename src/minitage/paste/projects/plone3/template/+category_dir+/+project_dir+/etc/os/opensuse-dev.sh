echo install pil dependencies
zypper install libjpeg-devel freetype2-devel libpng-devel

echo install lxml dependencies
zypper install  libxml2-devel libxslt-devel

echo install postgresql
zypper install postgresql-devel

zypper install libmysqlclient-devel

echo install ldap
zypper install openldap2-devel

echo install build tools
zypper install gcc43 gcc43-c++ make
