import re
import os
import codecs

from setuptools import setup, find_packages


requirements =[
    "future >= 0.15.0, < 1",
    "requests >= 2.5.2, < 3",
    "six >= 1.3.0, < 2",
    "websocket-client >= 0.32.0, < 1",
    "PyYAML >=3, < 4",
    "ago >=0.0.6, < 0.1",
    "python-dateutil >= 2, <3",
    "python-dockercloud >= 1, <2",
    "tabulate >= 0.7, <1"
]


def read(*parts):
    path = os.path.join(os.path.dirname(__file__), *parts)
    with codecs.open(path, encoding='utf-8') as fobj:
        return fobj.read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError('Unable to find version string.')

with open('./test-requirements.txt') as test_reqs_txt:
    test_requirements = [line for line in test_reqs_txt]

setup(
    name='docker-cloud',
    version=find_version('dockercloudcli', '__init__.py'),
    packages=find_packages(),
    install_requires=requirements,
    tests_require=test_requirements,
    entry_points={
        'console_scripts':
            ['docker-cloud = dockercloudcli.cli:main']
    },
    include_package_data=True,
    author='Docker, Inc.',
    author_email='info@docker.com',
    description='CLI for Docker Cloud',
    license='Apache v2',
    keywords='docker cloud cli',
    url='http://cloud.docker.com/',
    test_suite='tests',
)
