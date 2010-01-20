echo install pil dependencies
zypper install libjpeg freetype2 libpng3 libpng12-0

echo install lxml dependencies
zypper install libxml2 libxslt

echo install postgresql
zypper install postgresql postgresql-server postgresql-libs

zypper install mysql

echo install ldap
zypper install openldap2 openldap2-client

echo install memcached
zypper install memcached

echo word and pdf indexing binaries
zypper install wv wv2 xpdf

echo install build tools
zypper install gcc43 gcc43-c++ make
