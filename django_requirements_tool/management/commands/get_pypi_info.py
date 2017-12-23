import os
from django.core.management import BaseCommand
from django_test_tools.file_utils import serialize_data

from django_requirements_tool.exceptions import RequirementsToolException
from django_requirements_tool.pip.utils import get_pypi_info


class Command(BaseCommand):
    """
        $ python manage.py
    """

    def add_arguments(self, parser):
        parser.add_argument('output_path')
        # parser.add_argument("-l", "--list",
        #                     action='store_true',
        #                     dest="list",
        #                     help="List employees",
        #                     )
        # parser.add_argument("-a", "--assign",
        #                     action='store_true',
        #                     dest="assign",
        #                     help="Create unit assignments",
        #                     )
        #
        # parser.add_argument("--office",
        #                     dest="office",
        #                     help="Organizational unit short name",
        #                     default=None,
        #                     )
        # parser.add_argument("--start-date",
        #                     dest="start_date",
        #                     help="Start date for the assignment",
        #                     default=None,
        #                     )
        # parser.add_argument("--fiscal-year",
        #                     dest="fiscal_year",
        #                     help="Fiscal year for assignments",
        #                     default=None,
        #                     )
        parser.add_argument("-p", "--packages",
                         dest="packages",
                         help="Packages to get info for",
                         nargs='+',
                         )

    def handle(self, *args, **options):
        for package in options['packages']:
            try:
                filename = os.path.join(options.get('output_path'), '{}.json'.format(package))
                pypi_info = get_pypi_info(package)
                serialize_data(pypi_info, output_file=filename)
                self.stdout.write('Wrote {}'.format(filename))
            except RequirementsToolException as e:
                self.stderr.write(str(e))
