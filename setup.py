import os, sys
from setuptools import setup, find_packages
setupdir = os.path.abspath(
    os.path.dirname(__file__)
)
os.chdir(setupdir)

name='minitage.paste'
version = '1.3.1871'
                   

def read(rnames):
    return open(
        os.path.join(setupdir, rnames)
    ).read()

long_description = (
    read('README.rst')
    + '\n' +
    read('CHANGES.txt')
    + '\n'
)
if 'RST_TEST' in os.environ:
    print long_description
    sys.exit(0)


setup(
    name=name,
    version=version,
    description='PasteScripts to facilitate use of minitage and creation of minitage based projects sponsored by Makina Corpus.',
    long_description = long_description,
    classifiers=[
        "Framework :: Django",
        "Framework :: Pylons",
        "Framework :: Paste",
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3" ,
        "Framework :: Buildout",
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords='PasteScripts minitage',
    author='Mathieu Pasquet',
    author_email='kiorky@cryptelium.net',
    url='http://cheeseshop.python.org/pypi/%s' % name,
    license='BSD',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['minitage', name, '%s.instances' % name, '%s.projects' % name],
    include_package_data=True,
    zip_safe=False,
    install_requires = ['setuptools',
                        'PasteScript',
                        'ZopeSkel',
                        'zc.buildout',
                        'iniparse',
                        'Cheetah>1.0,<=2.2.1',],
    #tests_require = ['zope.testing'],
    # merged into django 'minitage.geodjango = minitage.paste.projects.geodjango:Template',
    entry_points = {
        'paste.paster_create_template' : [
            'minitage.dependency = minitage.paste.projects.dependency:Template',
            'minitage.django = minitage.paste.projects.django:Template',
            'minitage.pyramid = minitage.paste.projects.pyramid:Template',
            'minitage.egg = minitage.paste.projects.egg:Template',
            'minitage.plone25 = minitage.paste.projects.plone25:Template',
            'minitage.plone3 = minitage.paste.projects.plone3:Template',
            'minitage.plone4 = minitage.paste.projects.plone4:Template',
            'minitage.plone41 = minitage.paste.projects.plone41:Template',
            'minitage.plone42 = minitage.paste.projects.plone42:Template',
            'minitage.instances.apache = minitage.paste.instances.apache:Template',
            'minitage.instances.env = minitage.paste.instances.env:Template',
            'minitage.instances.postgresql = minitage.paste.instances.postgresql:Template',
            'minitage.instances.mysql = minitage.paste.instances.mysql:Template',
            'minitage.instances.nginx = minitage.paste.instances.nginx:Template',
            'minitage.instances.varnish = minitage.paste.instances.varnish:Template',
            'minitage.instances.varnish2 = minitage.paste.instances.varnish2:Template',
            'minitage.instances.paste-initd = minitage.paste.instances.pasteinitd:Template',
        ]
    },
)



