from unittest import mock

from django.test import SimpleTestCase
from django_test_tools.assert_utils import write_assertions
from django_test_tools.file_utils import temporary_file, serialize_data
import environ
from django_requirements_tool.exceptions import RequirementsToolException
from django_requirements_tool.pip.utils import parse_specifier, list_outdated_libraries, update_outdated_libraries, \
    get_latest_version, read_requirement_file, get_pypi_info, find_outdated_libraries
import json

class TestParseSpecifier(SimpleTestCase):
    def test_parse_specifier(self):
        result = parse_specifier('==2.1.1')
        self.assertEqual(result[0], '==')
        self.assertEqual(result[1], '2.1.1')

    def test_parse_specifier(self):
        with self.assertRaises(ValueError) as context:
            parse_specifier('2.1.1')

        self.assertEqual(str(context.exception), 'Invalid speficier "2.1.1"')

    @mock.patch('django_requirements_tool.pip.utils.pip.main')
    def test_list_outdated_libraries(self, mock_pip_main):
        main_result = 'binaryornot (0.4.3) - Latest: 1.4.4 [wheel]\nchardet (3.0.2) - Latest: 3.0.4 [wheel]\n' \
                       'cookiecutter (1.5.1) - Latest: 1.6.0 [wheel]\ncoverage (4.4.1) - Latest: 4.4.2 [wheel]\n' \
                       'Faker (0.7.17) - Latest: 0.8.7 [wheel]\nflake8 (3.3.0) - Latest: 3.5.0 [wheel]\n' \
                       'Jinja2 (2.9.6) - Latest: 2.10 [wheel]\nopenpyxl (2.4.8) - Latest: 2.4.9 [sdist]\n' \
                       'pbr (3.0.1) - Latest: 3.1.1 [wheel]\npluggy (0.4.0) - Latest: 0.5.2 [sdist]\n' \
                       'py (1.4.33) - Latest: 1.5.2 [wheel]\npyflakes (1.5.0) - Latest: 1.6.0 [wheel]\n' \
                       'pylint (1.7.2) - Latest: 1.7.4 [wheel]\npython-dateutil (2.6.0) - Latest: 2.6.1 [wheel]\n' \
                       'pytz (2017.2) - Latest: 2017.3 [wheel]\nradon (2.0.2) - Latest: 2.1.1 [wheel]\n' \
                       'requests (2.14.2) - Latest: 2.18.4 [wheel]\nsetuptools (36.0.1) - Latest: 37.0.0 [wheel]\n' \
                       'six (1.10.0) - Latest: 1.11.0 [wheel]\ntox (2.7.0) - Latest: 2.9.1 [wheel]\n' \
                       'wrapt (1.10.10) - Latest: 1.10.11 [sdist]\n' \
                       'DEPRECATION: The default format will switch to columns in the future. '  \
                       'You can use --format=(legacy|columns) (or define a format=(legacy|columns) in your pip.conf '  \
                       'under the [list] section) to disable this warning.\n'

        mock_capture = mock.Mock()
        mock_capture.return_value = mock_capture
        mock_capture.__enter__ = mock.Mock(return_value=(main_result, ['\n']))
        mock_capture.__exit__ = mock.Mock(return_value=(mock.Mock(), None))


        with mock.patch('django_requirements_tool.pip.utils.capture', mock_capture):
            outdated = list_outdated_libraries()
        mock_pip_main.assert_called_with(['list', '--outdated'])

        self.assertEqual(len(outdated), 21)
        self.assertEqual(outdated['binaryornot']['current_version'], '0.4.3')
        self.assertEqual(outdated['binaryornot']['name'], 'binaryornot')
        self.assertEqual(outdated['binaryornot']['new_version'], '1.4.4')
        self.assertEqual(outdated['chardet']['current_version'], '3.0.2')
        self.assertEqual(outdated['chardet']['name'], 'chardet')
        self.assertEqual(outdated['chardet']['new_version'], '3.0.4')
        self.assertEqual(outdated['cookiecutter']['current_version'], '1.5.1')
        self.assertEqual(outdated['cookiecutter']['name'], 'cookiecutter')
        self.assertEqual(outdated['cookiecutter']['new_version'], '1.6.0')
        self.assertEqual(outdated['coverage']['current_version'], '4.4.1')
        self.assertEqual(outdated['coverage']['name'], 'coverage')
        self.assertEqual(outdated['coverage']['new_version'], '4.4.2')
        self.assertEqual(outdated['faker']['current_version'], '0.7.17')
        self.assertEqual(outdated['faker']['name'], 'faker')
        self.assertEqual(outdated['faker']['new_version'], '0.8.7')
        self.assertEqual(outdated['flake8']['current_version'], '3.3.0')
        self.assertEqual(outdated['flake8']['name'], 'flake8')
        self.assertEqual(outdated['flake8']['new_version'], '3.5.0')
        self.assertEqual(outdated['jinja2']['current_version'], '2.9.6')
        self.assertEqual(outdated['jinja2']['name'], 'jinja2')
        self.assertEqual(outdated['jinja2']['new_version'], '2.10')
        self.assertEqual(outdated['openpyxl']['current_version'], '2.4.8')
        self.assertEqual(outdated['openpyxl']['name'], 'openpyxl')
        self.assertEqual(outdated['openpyxl']['new_version'], '2.4.9')
        self.assertEqual(outdated['pbr']['current_version'], '3.0.1')
        self.assertEqual(outdated['pbr']['name'], 'pbr')
        self.assertEqual(outdated['pbr']['new_version'], '3.1.1')
        self.assertEqual(outdated['pluggy']['current_version'], '0.4.0')
        self.assertEqual(outdated['pluggy']['name'], 'pluggy')
        self.assertEqual(outdated['pluggy']['new_version'], '0.5.2')
        self.assertEqual(outdated['py']['current_version'], '1.4.33')
        self.assertEqual(outdated['py']['name'], 'py')
        self.assertEqual(outdated['py']['new_version'], '1.5.2')
        self.assertEqual(outdated['pyflakes']['current_version'], '1.5.0')
        self.assertEqual(outdated['pyflakes']['name'], 'pyflakes')
        self.assertEqual(outdated['pyflakes']['new_version'], '1.6.0')
        self.assertEqual(outdated['pylint']['current_version'], '1.7.2')
        self.assertEqual(outdated['pylint']['name'], 'pylint')
        self.assertEqual(outdated['pylint']['new_version'], '1.7.4')
        self.assertEqual(outdated['python-dateutil']['current_version'], '2.6.0')
        self.assertEqual(outdated['python-dateutil']['name'], 'python-dateutil')
        self.assertEqual(outdated['python-dateutil']['new_version'], '2.6.1')
        self.assertEqual(outdated['pytz']['current_version'], '2017.2')
        self.assertEqual(outdated['pytz']['name'], 'pytz')
        self.assertEqual(outdated['pytz']['new_version'], '2017.3')
        self.assertEqual(outdated['radon']['current_version'], '2.0.2')
        self.assertEqual(outdated['radon']['name'], 'radon')
        self.assertEqual(outdated['radon']['new_version'], '2.1.1')
        self.assertEqual(outdated['requests']['current_version'], '2.14.2')
        self.assertEqual(outdated['requests']['name'], 'requests')
        self.assertEqual(outdated['requests']['new_version'], '2.18.4')
        self.assertEqual(outdated['setuptools']['current_version'], '36.0.1')
        self.assertEqual(outdated['setuptools']['name'], 'setuptools')
        self.assertEqual(outdated['setuptools']['new_version'], '37.0.0')
        self.assertEqual(outdated['six']['current_version'], '1.10.0')
        self.assertEqual(outdated['six']['name'], 'six')
        self.assertEqual(outdated['six']['new_version'], '1.11.0')
        self.assertEqual(outdated['tox']['current_version'], '2.7.0')
        self.assertEqual(outdated['tox']['name'], 'tox')
        self.assertEqual(outdated['tox']['new_version'], '2.9.1')
        self.assertEqual(outdated['wrapt']['current_version'], '1.10.10')
        self.assertEqual(outdated['wrapt']['name'], 'wrapt')
        self.assertEqual(outdated['wrapt']['new_version'], '1.10.11')

class TestReadRequirementFile(SimpleTestCase):

    @classmethod
    def setUpClass(cls):
        super(TestReadRequirementFile, cls).setUpClass()
        cls.pip_main_result = 'Django (1.11.3) - Latest: 2.1.0 [wheel]\ncelery (4.0.1) - Latest: 4.10.1 [wheel]\n' \
                      'cookiecutter (1.5.1) - Latest: 1.6.0 [wheel]\ncoverage (4.4.1) - Latest: 4.4.2 [wheel]\n' \
                      'Faker (0.7.17) - Latest: 0.8.7 [wheel]\nflake8 (3.3.0) - Latest: 3.5.0 [wheel]\n' \
                      'Jinja2 (2.9.6) - Latest: 2.10 [wheel]\nopenpyxl (2.4.8) - Latest: 2.4.9 [sdist]\n' \
                      'pbr (3.0.1) - Latest: 3.1.1 [wheel]\npluggy (0.4.0) - Latest: 0.5.2 [sdist]\n' \
                      'py (1.4.33) - Latest: 1.5.2 [wheel]\npyflakes (1.5.0) - Latest: 1.6.0 [wheel]\n' \
                      'pylint (1.7.2) - Latest: 1.7.4 [wheel]\npython-dateutil (2.6.0) - Latest: 2.6.1 [wheel]\n' \
                      'pytz (2017.2) - Latest: 2017.3 [wheel]\nradon (2.0.2) - Latest: 2.1.1 [wheel]\n' \
                      'requests (2.14.2) - Latest: 2.18.4 [wheel]\nsetuptools (36.0.1) - Latest: 37.0.0 [wheel]\n' \
                      'six (1.10.0) - Latest: 1.11.0 [wheel]\ntox (2.7.0) - Latest: 2.9.1 [wheel]\n' \
                      'wrapt (1.10.10) - Latest: 1.10.11 [sdist]\n' \
                      'DEPRECATION: The default format will switch to columns in the future. ' \
                      'You can use --format=(legacy|columns) (or define a format=(legacy|columns) in your pip.conf ' \
                      'under the [list] section) to disable this warning.\n'

    def setUp(self):
        self.requirements = list()
        self.requirements.append('django==1.11.3 # pyup: >=1.10,<1.11\n')
        self.requirements.append('celery==4.0.1\n')
        self.requirements.append('redis>=2.10.5\n')

    @mock.patch('django_requirements_tool.pip.utils.pip.main')
    @temporary_file(extension='txt', delete_on_exit=True)
    def test_update_outdated_libraries(self, mock_pip_main):
        filename = self.test_update_outdated_libraries.filename
        with open(filename, 'w', encoding='utf-8') as req_file:
            req_file.writelines(self.requirements)

        mock_capture = mock.Mock()
        mock_capture.return_value = mock_capture
        mock_capture.__enter__ = mock.Mock(return_value=(self.pip_main_result, ['\n']))
        mock_capture.__exit__ = mock.Mock(return_value=(mock.Mock(), None))

        with mock.patch('django_requirements_tool.pip.utils.capture', mock_capture):
            changes = update_outdated_libraries(filename)

        mock_pip_main.assert_called_with(['list', '--outdated'])

        self.assertEqual(len(changes), 2)
        self.assertRegex(changes[0]['filename'], r'test_update_outdated_libraries_\d{8}_\d{4}\.txt')
        self.assertEqual(changes[0]['library_name'], 'django')
        self.assertEqual(changes[0]['line_no'], 0)
        self.assertEqual(changes[0]['new'], 'django==2.1.0')
        self.assertEqual(changes[0]['previous'], 'django==1.11.3 # pyup: >=1.10,<1.11')
        self.assertRegex(changes[1]['filename'], r'test_update_outdated_libraries_\d{8}_\d{4}\.txt')
        self.assertEqual(changes[1]['library_name'], 'celery')
        self.assertEqual(changes[1]['line_no'], 1)
        self.assertEqual(changes[1]['new'], 'celery==4.10.1')
        self.assertEqual(changes[1]['previous'], 'celery==4.0.1')

    @temporary_file(extension='txt', delete_on_exit=True)
    def test_read_requirement_file(self):
        filename = self.test_read_requirement_file.filename

        with open(filename, 'w', encoding='utf-8') as req_file:
            req_file.writelines(self.requirements)

        requirements = read_requirement_file(filename)
        #write_assertions(requirements, 'requirements')
        self.assertEqual(requirements['celery']['comes_from']['file_indicator'], '-r')
        self.assertTrue(filename in requirements['celery']['comes_from']['filename'])
        self.assertEqual(requirements['celery']['comes_from']['line_no'], 2)
        self.assertTrue(filename in requirements['celery']['comes_from']['value'])
        self.assertEqual(requirements['celery']['name'], 'celery')
        self.assertEqual(requirements['celery']['operator'], '==')
        self.assertEqual(requirements['celery']['version'], '4.0.1')
        self.assertEqual(requirements['django']['comes_from']['file_indicator'], '-r')
        self.assertTrue(filename in requirements['django']['comes_from']['filename'])
        self.assertEqual(requirements['django']['comes_from']['line_no'], 1)
        self.assertTrue(filename in requirements['django']['comes_from']['value'])
        self.assertEqual(requirements['django']['name'], 'django')
        self.assertEqual(requirements['django']['operator'], '==')
        self.assertEqual(requirements['django']['version'], '1.11.3')
        self.assertEqual(requirements['redis']['comes_from']['file_indicator'], '-r')
        self.assertTrue(filename in requirements['redis']['comes_from']['filename'])
        self.assertEqual(requirements['redis']['comes_from']['line_no'], 3)
        self.assertTrue(filename in requirements['redis']['comes_from']['value'])
        self.assertEqual(requirements['redis']['name'], 'redis')
        self.assertEqual(requirements['redis']['operator'], '>=')
        self.assertEqual(requirements['redis']['version'], '2.10.5')

def mocked_requests_get(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code, reason=None):
            self.json_data = json_data
            self.status_code = status_code
            self.reason = reason

        def json(self):
            return self.json_data

    def _load_fixture_data(filename):
        json_file = (environ.Path(__file__) - 1).path('fixtures', filename).root
        with open(json_file, 'r', encoding='utf-8') as file:
            json_data = json.load(file)
        return json_data
    url_pattern ='https://pypi.python.org/pypi/{0}/json'
    if args[0] == url_pattern.format('django'):
        data = _load_fixture_data('django.json')
        return MockResponse(data,  200)
    if args[0] == url_pattern.format('django-test-tools'):
        data = _load_fixture_data('django_test_tools_20171204_2116.json')
        return MockResponse(data,  200)
    elif args[0] == url_pattern.format('celery'):
        data = _load_fixture_data('celery_20171204_2118.json')
        return MockResponse(data, 200)
    elif args[0] == url_pattern.format('redis'):
        data = _load_fixture_data('redis_20171223_1013.json')
        return MockResponse(data, 200)

    return MockResponse(None, 404, reason='Not Found (no releases)')

class TestPyPiTools(SimpleTestCase):


    @mock.patch('django_requirements_tool.pip.utils.requests.get', side_effect=mocked_requests_get)
    def test_get_latest_version(self, mock_get):
        version = get_latest_version('celery')
        self.assertEqual(version, '4.1.0')
        mock_get.assert_called_with('https://pypi.python.org/pypi/celery/json')

    @mock.patch('django_requirements_tool.pip.utils.requests.get', side_effect=mocked_requests_get)
    def test_get_latest_version_error(self, mock_get):
        with self.assertRaises(RequirementsToolException) as context:
            get_latest_version('celery-blad')
        self.assertEqual(str(context.exception), 'Could not connect to https://pypi.python.org/pypi/celery-blad/json. Status 404. Not Found (no releases)')

    @mock.patch('django_requirements_tool.pip.utils.requests.get', side_effect=mocked_requests_get)
    def test_get_pypi_info(self, mock_get):
        package_name = 'django-test-tools'
        pypi_info = get_pypi_info(package_name)
        #serialize_data(pypi_info,base_filename=package_name.replace('-', '_'))
        self.assertEqual(pypi_info['info']['author'], 'Bruce Wayne')
        mock_get.assert_called_with('https://pypi.python.org/pypi/django-test-tools/json')


class TestFindRequirements(SimpleTestCase):

    def setUp(self):
        self.requirements = list()
        self.requirements.append('django==1.11.3 # pyup: >=1.10,<1.11\n')
        self.requirements.append('celery==4.0.1\n')
        self.requirements.append('redis>=2.10.5\n')

    @temporary_file(extension='txt', delete_on_exit=True)
    @mock.patch('django_requirements_tool.pip.utils.requests.get', side_effect=mocked_requests_get)
    def test_find_outdated_libraries(self, mock_get):
        filename = self.test_find_outdated_libraries.filename
        with open(filename, 'w', encoding='utf-8') as req_file:
            req_file.writelines(self.requirements)
        results = find_outdated_libraries(filename)
        serialize_data(results, base_filename='outdated_in_req_file')
        mock_get.assert_called_with('https://pypi.python.org/pypi/django-test-tools/json')
