import re

import os
from django.conf import settings
from django.core.management import call_command
from django.test import SimpleTestCase
from django_test_tools.mixins import TestCommandMixin


class GetPyPiInfoCommand(TestCommandMixin, SimpleTestCase):
    def test_get_pypi_info(self):
        call_command('get_pypi_info',
                     settings.TEST_OUTPUT_PATH,
                     packages=['django'],
                     stdout=self.content,
                     stderr=self.error_content)
        results = self.get_results()
        regexp = re.compile(r'Wrote\s([\w\/-]*\.json)')
        match = regexp.match(results[0])
        self.assertTrue(os.path.exists(match.group(1)))
        os.remove(match.group(1))
