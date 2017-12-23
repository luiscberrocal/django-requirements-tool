import contextlib
from operator import itemgetter

import pkg_resources

import pip
import re

import requests

from django_test_tools.file_utils import serialize_data

from django_requirements_tool.exceptions import RequirementsToolException


@contextlib.contextmanager
def capture():
    import sys
    from io import StringIO
    oldout, olderr = sys.stdout, sys.stderr
    try:
        out=[StringIO(), StringIO()]
        sys.stdout,sys.stderr = out
        yield out
    finally:
        sys.stdout,sys.stderr = oldout, olderr
        out[0] = out[0].getvalue()
        out[1] = out[1].getvalue()


def parse_pip_list(line):
    regexp = re.compile(r'([\w\-]*)\s\(([\w\-_\.]*)\)\s\-\sLatest:\s([\w\-_\.]*)\s\[([a-z]*)\]')
    match = regexp.match(line)
    if match:
        library = dict()
        library['name'] = match.group(1).lower()
        library['current_version'] = match.group(2)
        library['new_version'] = match.group(3)
        return library
    return None


def get_latest_version(package_name):
    pypi_info = get_pypi_info(package_name)
    versions = sorted(pypi_info["releases"], key=pkg_resources.parse_version)
    return versions[-1]

def get_pypi_info(package_name):
    url = 'https://pypi.python.org/pypi/{}/json'.format(package_name)
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 404:
        raise RequirementsToolException(response.reason)
    else:
        msg = 'Received an unsupported status {} from {}'.format(response.status_code, url)
        raise RequirementsToolException(msg)


def parse_comes_from(comes_from):
    regexp = re.compile(r'(\-r)\s([/\w\.\-]*)\s\(line\s(\d*)\)')
    match = regexp.match(comes_from)
    if match:
        return match.group(1), match.group(2), int(match.group(3))
    else:
        raise ValueError('Invalid comes from "{}"'.format(comes_from))


def parse_specifier(specifier):
    regexp = re.compile(r'((?:[=>])=)([\w\-_\.]*)')
    match = regexp.match(specifier)
    if match:
        return match.group(1), match.group(2)
    else:
        raise ValueError('Invalid speficier "{}"'.format(specifier))


def read_requirement_file(req_file):
    """
    Will read a requirement file and will return a dictionary with a key for every requirement.
    Every requirement will have the following keys:

    * **comes_from** has four keys:

        * **file_indicator**: to indicate if the requirement is recursive whe the pip install command was ran.
        usually -r
        * **filename**: full path to the requirement file where the requirement was found.
        * **line_no**: Line number where the requirement is found.
        * **value**: This what the pip library returns. Its just used for debug pourposes.

    * **name**: Name of the library.
    * **operator**: the operator for the version ==, >=. Current version only supporst this two operators. See
        parse_specifier method.
    * **version**: version number.

    from a requirement file like::

        celery==4.0.1
        django==1.11.3
        redis>=2.10.5

    wille generate a dictionary like:

    ..code-block:: python

        {
            "celery": {
                "comes_from": {
                    "file_indicator": "-r",
                    "filename": "requirements/requirements.txt",
                    "line_no": 2,
                    "value": "-r requirements/requirements.txt (line 2)"
                },
                "name": "celery",
                "operator": "==",
                "version": "4.0.1"
            },
            "django": {
                "comes_from": {
                    "file_indicator": "-r",
                    "filename": "requirements/requirements.txt",
                    "line_no": 1,
                    "value": "-r requirements/requirements.txt (line 1)"
                },
                "name": "django",
                "operator": "==",
                "version": "1.11.3"
            },
            "redis": {
                "comes_from": {
                    "file_indicator": "-r",
                    "filename": "requirements/requirements.txt",
                    "line_no": 3,
                    "value": "-r requirements/requirements.txt (line 3)"
                },
                "name": "redis",
                "operator": ">=",
                "version": "2.10.5"
            }
        }
    :param req_file:
    :return:
    """
    requirements = dict()
    for item in pip.req.parse_requirements(req_file, session="somesession"):
        if isinstance(item, pip.req.InstallRequirement):
            requirement = dict()
            requirement['name'] = item.name
            if len(str(item.req.specifier)) > 0:
                operator, version = parse_specifier(str(item.req.specifier))
                requirement['operator'] = operator
                requirement['version'] = version
            requirement['comes_from'] = dict()
            requirement['comes_from']['value'] = item.comes_from
            file_indicator, filename, line_no = parse_comes_from(item.comes_from)
            requirement['comes_from']['file_indicator'] = file_indicator
            requirement['comes_from']['filename'] = filename
            requirement['comes_from']['line_no'] = line_no

            requirements[item.name] = requirement
    return requirements


def list_outdated_libraries():
    """
    Will run the command pip list --outdated parse the result and return a dictionary of packages that are installed
    but outdated.

    for example the function would return a dictionary like this:

    .. code-block:: python


        {
            "binaryornot": {
                "current_version": "0.4.3",
                "name": "binaryornot",
                "new_version": "1.4.4"
            },
            "chardet": {
                "current_version": "3.0.2",
                "name": "chardet",
                "new_version": "3.0.4"
            },
            "cookiecutter": {
                "current_version": "1.5.1",
                "name": "cookiecutter",
                "new_version": "1.6.0"
            }
        }
    :return: dict with outdated libaries.
    """
    with capture() as out:
        pip.main(['list', '--outdated'])
    library_lines = out[0].split('\n')
    outdated_libraries = dict()
    for line in library_lines:
        library = parse_pip_list(line)
        if library is not None:
            outdated_libraries[library['name']] = library
    return outdated_libraries


def update_outdated_libraries(requirement_file, **kwargs):
    """
    Updates the requirements to their latest version.

    :param requirement_file: String with the path to the requirement fiel
    :param kwargs:
    :return: list of dictionaries containing the changes
    """
    requirements = read_requirement_file(requirement_file)
    outdated_libraries = list_outdated_libraries()
    changes = list()
    for outdated_library in outdated_libraries.values():
        library_name = outdated_library['name']
        if requirements.get(library_name):
            change = dict()
            change['library_name'] = library_name
            change['filename'] = requirements[library_name]['comes_from']['filename']
            line_no = requirements[library_name]['comes_from']['line_no'] - 1
            operator = requirements[library_name]['operator']
            with open(change['filename'], 'r') as file:
                data = file.readlines()
            new_value = '{}{}{}\n'.format(library_name, operator, outdated_library['new_version'])
            change['previous'] = data[line_no].strip('\n')
            change['new'] = new_value.strip('\n')
            data[line_no] = new_value
            with open(change['filename'], 'w') as file:
                file.writelines(data)
            change['line_no'] = line_no
            changes.append(change)
    sorted_changes = sorted(changes, key=itemgetter('library_name'), reverse=True)
    return sorted_changes

