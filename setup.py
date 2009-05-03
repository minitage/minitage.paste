import os
from setuptools import setup, find_packages
setupdir = os.path.abspath(
    os.path.dirname(__file__)
)
os.chdir(setupdir)

name='minitage.paste'
version = '1.1'

def read(rnames):
    return open(
        os.path.join(setupdir, rnames)
    ).read()

setup(
    name=name,
    version=version,
    description='PasteScripts to facilitate use of minitage and creation of minitage based projects.',
    long_description= (
        read('README.txt')
        + '\n' +
        read('CHANGES.txt')
        + '\n'
    ),
    classifiers=[
        "Framework :: Django",
        "Framework :: Pylons",
        "Framework :: Paste",
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3" ,
        "Framework :: Buildout",
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords='PasteScripts minitage',
    author='Mathieu Pasquet',
    author_email='kiorky@cryptelium.net',
    url='http://cheeseshop.python.org/pypi/%s' % name,
    license='GPL',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['minitage', name],
    include_package_data=True,
    zip_safe=False,
    install_requires = ['setuptools',
                        'PasteScript',
                        'zc.buildout',
                        'Cheetah',
                        'minitage.core'],
    #tests_require = ['zope.testing'],
    # merged into django 'minitage.geodjango = minitage.paste.projects.geodjango:Template',
    entry_points = {
        'paste.paster_create_template' : [
            'minitage.dependency = minitage.paste.projects.dependency:Template',
            'minitage.django = minitage.paste.projects.django:Template',
            'minitage.egg = minitage.paste.projects.egg:Template',
            'minitage.plone25 = minitage.paste.projects.plone25:Template',
            'minitage.plone3 = minitage.paste.projects.plone3:Template',
            'minitage.profils.env = minitage.paste.profils.env:Template',
            'minitage.profils.postgresql = minitage.paste.profils.postgresql:Template',
            'minitage.profils.varnish = minitage.paste.profils.varnish:Template',
            'minitage.profils.varnish2 = minitage.paste.profils.varnish2:Template',
            'minitage.profils.paste-initd = minitage.paste.profils.pasteinitd:Template',
            'minitage.pylons = minitage.paste.projects.pylons:Template',
            'minitage.zope2 = minitage.paste.projects.zope2:Template',
            'minitage.zope3 = minitage.paste.projects.zope3:Template',
        ]
    },
)

