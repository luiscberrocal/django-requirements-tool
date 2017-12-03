=============================
Django Requirements Tool
=============================

.. image:: https://badge.fury.io/py/django-requirements-tool.svg
    :target: https://badge.fury.io/py/django-requirements-tool

.. image:: https://travis-ci.org/luiscberrocal/django-requirements-tool.svg?branch=master
    :target: https://travis-ci.org/luiscberrocal/django-requirements-tool

.. image:: https://codecov.io/gh/luiscberrocal/django-requirements-tool/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/luiscberrocal/django-requirements-tool

A Django app to keep track of the requiremnts in your projects.

Documentation
-------------

The full documentation is at https://django-requirements-tool.readthedocs.io.

Quickstart
----------

Install Django Requirements Tool::

    pip install django-requirements-tool

Add it to your `INSTALLED_APPS`:

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'django_requirements_tool.apps.DjangoRequirementsToolConfig',
        ...
    )

Add Django Requirements Tool's URL patterns:

.. code-block:: python

    from django_requirements_tool import urls as django_requirements_tool_urls


    urlpatterns = [
        ...
        url(r'^', include(django_requirements_tool_urls)),
        ...
    ]

Features
--------

* TODO

Running Tests
-------------

Does the code actually work?

::

    source <YOURVIRTUALENV>/bin/activate
    (myenv) $ pip install tox
    (myenv) $ tox

Credits
-------

Tools used in rendering this package:

*  Cookiecutter_
*  `cookiecutter-djangopackage`_

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`cookiecutter-djangopackage`: https://github.com/pydanny/cookiecutter-djangopackage
