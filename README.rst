****************************************************************
Paste Scripts to install profiles into minitage based projects
****************************************************************

.. contents::

What is minitage.paste
=======================

Those are PasteScripts to help creating out projects living inside minitage.
You ll find in there:

Makina Corpus sponsored software
======================================
|makinacom|_

* `Planet Makina Corpus <http://www.makina-corpus.org>`_
* `Contact us <mailto:python@makina-corpus.org>`_

.. |makinacom| image:: http://depot.makina-corpus.org/public/logo.gif
.. _makinacom:  http://www.makina-corpus.com


Projects templates
===================

    - minitage.zope3: A sample layout for a zope 3 application
    - minitage.plone25: A sample layout for a plone 25 application
    - minitage.plone3: A sample layout for a plone 3 application
    - minitage.tg: A sample layout for a turbogears application
    - minitage.django: A sample layout for a django application
    - minitage.geodjango: A sample layout for a geo-django application
    - minitage.dependency: A sample layout for a compiled dependency
    - minitage.egg: A sample layout for an egg dependency
    - minitage.pyramid : A simple layout for a pyramid project

Projects  instances
=======================

    - minitage.instances.apache: create an apache instance.
    - minitage.instances.nginx: create a nginx instance.
    - minitage.instances.varnish: create a varnish instance with or without a sample
      configuration file toward zope/plone.
    - minitage.instances.varnish2: create a varnish2 instance with or without a sample
      configuration file toward zope/plone. 
    - minitage.instances.postgresql: create a postgresql instance in the sys dir of your
      project
    - minitage.instances.mysql: create a mysql instance in the sys dir of your
      project

    - minitage.instances.paste-initd: create a paste initd file and logrotated
      stuff in the sys dir of your project
    - minitage.instances.env: create a `share/minitage/minitage.env` file inside the
      sysdir of the project. You ll can source it and have into your environment
      the path and libraries from the registred dependencies of your project.



Extras
==============
Those templates that need intrusives dependencies like pyopenssl that need to be
compiled. That why there are not included in the main package.

See ``minitage.paste.instances.extras`` on Pypi..

     - minitage.instances.openldap: create a openldap instance in the sys dir of your
       project
     - minitage.instances.cas: create a CAS server instance in the sys dir of your project

Usage
======

Use throught paster::

    easy_install minitage.paste
    paster create -t [template_name] target_project [opt=n opt2=n]

This will create a new project and a new minilay in your current minitage.

Here must come as dependencies::

    minitage.core
    zc.buildout
    PasteScripts
    Cheetah


