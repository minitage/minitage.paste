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

    - minitage.plone42: A sample layout for a plone 4.2 application
    - minitage.plone41: A sample layout for a plone 4.1 application
    - minitage.plone4: A sample layout for a plone 4 application
    - minitage.plone3: A sample layout for a plone 3 application
    - minitage.django: A sample layout for a django application
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

Use throught webbuilder, see `this doc <http://pypi.python.org/pypi/collective.generic.webbuilder>`_


Use throught paster::

    easy_install minitage.paste
    paster create -t [template_name] target_project [opt=n opt2=n]

This will create a new project and a new minilay in your current minitage.

Here must come as dependencies::

    minitage.core
    zc.buildout
    PasteScripts
    Cheetah


DISCLAIMER - ABANDONED/UNMAINTAINED CODE / DO NOT USE
=======================================================

This project has been transfered to Makina Corpus <freesoftware@makina-corpus.com> ( https://makina-corpus.com ).

minitage project was terminated in 2013. Consequently, this repository and all associated resources (including related projects, code, documentation, and distributed packages such as Docker images, PyPI packages, etc.) are now explicitly declared **unmaintained** and **abandoned**.

I would like to remind everyone that this project’s free license has always been based on the principle that the software is provided "AS-IS", without any warranty or expectation of liability or maintenance from the maintainer.
As such, it is used solely at the user's own risk, with no warranty or liability from the maintainer, including but not limited to any damages arising from its use.

Due to the enactment of the Cyber Resilience Act (EU Regulation 2024/2847), which significantly alters the regulatory framework, including penalties of up to €15M, combined with its demands for **unpaid** and **indefinite** liability, it has become untenable for me to continue maintaining all my Open Source Projects as a natural person.
The new regulations impose personal liability risks and create an unacceptable burden, regardless of my personal situation now or in the future, particularly when the work is done voluntarily and without compensation.

**No further technical support, updates (including security patches), or maintenance, of any kind, will be provided.**

These resources may remain online, but solely for public archiving, documentation, and educational purposes.

Users are strongly advised not to use these resources in any active or production-related projects, and to seek alternative solutions that comply with the new legal requirements (EU CRA).

**Using these resources outside of these contexts is strictly prohibited and is done at your own risk.**

Regarding the potential transfer of the project to another entity, discussions are ongoing, but no final decision has been made yet. As a last resort, if the project and its associated resources are not transferred, I may begin removing any published resources related to this project (e.g., from PyPI, Docker Hub, GitHub, etc.) starting **March 15, 2025**, especially if the CRA’s risks remain disproportionate.

