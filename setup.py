import os
from setuptools import setup, find_packages
setupdir = os.path.abspath(
    os.path.dirname(__file__)
) 
os.chdir(setupdir)

name='minitage.paste'
version = '0.0.1'

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
        'Framework :: Buildout',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords='development buildout recipe',
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
    entry_points = {
        'paste.paster_create_template' : [
            'minitage.pgsql = minitage.paste.profils.postgresql:Template',
            'minitage.env = minitage.paste.profils.env:Template',
        ]
    },
)

