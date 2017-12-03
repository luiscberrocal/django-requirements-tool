# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django.conf.urls import url, include

from django_requirements_tool.urls import urlpatterns as django_requirements_tool_urls

urlpatterns = [
    url(r'^', include(django_requirements_tool_urls, namespace='django_requirements_tool')),
]
