****************************************************************
Paste Scripts to install profiles into minitage based projects
****************************************************************

.. contents::

What is minitage.paste
=======================

Those are PasteScripts to help creating out projects living inside minitage.
You ll find in there:

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
    - minitage.pylons : A simple layout for a pylons project

Projects profiles
==================

    - minitage.profils.varnish: create a varnish instance with or without a sample
      configuration file toward zope/plone.
    - minitage.profils.postgresql: create a postgresql instance in the sys dir of your
      project
    - minitage.profils.paste-initd: create a paste initd file and logrotated
      stuff in the sys dir of your project 
    - minitage.profils.env: create a `share/minitage/minitage.env` file inside the
      sysdir of the project. You ll can source it and have into your environment
      the path and libraries from the registred dependencies of your project.

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


