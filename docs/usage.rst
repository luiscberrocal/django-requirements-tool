=====
Usage
=====

To use Django Requirements Tool in a project, add it to your `INSTALLED_APPS`:

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
