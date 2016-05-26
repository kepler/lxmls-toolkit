#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Based on https://github.com/pypa/sampleproject/blob/master/setup.py."""
from __future__ import unicode_literals
# To use a consistent encoding
import codecs
import os
import sys

from setuptools import find_packages
from distutils.core import setup

# Shortcut for building/publishing to Pypi
if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist bdist_wheel upload')
    sys.exit()


def parse_reqs(req_path='./requirements.txt'):
    """Recursively parse requirements from nested pip files."""
    install_requires = []
    with codecs.open(req_path, 'r') as handle:
        # remove comments and empty lines
        lines = (line.strip() for line in handle
                 if line.strip() and not line.startswith('#'))

        for line in lines:
            # check for nested requirements files
            if line.startswith('-r'):
                # recursively call this function
                install_requires += parse_reqs(req_path=line[3:])
            elif line.startswith('-e'):
                # e.g., -e git+https://github.com/maciejkula/glove-python@master#egg=glove-0.0.1
                egg = line[3:].split('#')[1][4:]  # egg=
                install_requires.append(egg.replace('-', '==', 1))
            else:
                # add the line as a new requirement
                install_requires.append(line)

    return install_requires


def parse_reqs_links(req_path='./requirements.txt'):
    """Recursively parse requirements from nested pip files."""
    dependency_links = []
    with codecs.open(req_path, 'r') as handle:
        # remove comments and empty lines
        lines = (line.strip() for line in handle
                 if line.strip() and not line.startswith('#'))

        for line in lines:
            # check for nested requirements files
            if line.startswith('-r'):
                # recursively call this function
                dependency_links += parse_reqs_links(req_path=line[3:])
            elif line.startswith('-e'):
                dependency_links.append(line[3:])
            else:
                # ignore
                pass

    return dependency_links


def parse_readme():
    """Parse contents of the README."""
    # Get the long description from the relevant file
    here = os.path.abspath(os.path.dirname(__file__))
    readme_path = os.path.join(here, 'README.md')
    with codecs.open(readme_path, encoding='utf-8') as handle:
        long_description = handle.read()

    return long_description


package_data = {
    'lxmls.readers': ['*.map']
}

setup(
    name='LXMLS_Toolkit',

    # Versions should comply with PEP440. For a discussion on
    # single-sourcing the version across setup.py and the project code,
    # see http://packaging.python.org/en/latest/tutorial.html#version
    version='0.0.2',

    description='Machine Learning and Natural Language toolkit',
    long_description=parse_readme(),
    # What does your project relate to? Separate with spaces.
    keywords='machine learning',
    author="LXMLS-team",
    author_email="lxmls-2013-org@googlegroups.com",
    license='MIT',

    # The project's main homepage
    url='https://github.com/LxMLS/lxmls-toolkit',

    packages=find_packages(exclude=('labs*', 'tests*', 'docs', 'examples')),

    # If there are data files included in your packages that need to be
    # installed, specify them here.
    include_package_data=True,
    # package_data=package_data,
    zip_safe=True,

    # Install requirements loaded from ``requirements.txt``
    install_requires=parse_reqs(),
    # Deal if packages from git repositories
    dependency_links=parse_reqs_links(),

    # test_suite='tests',

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and
    # allow pip to create the appropriate form of executable for the
    # target platform.
    # entry_points=dict(
    #     console_scripts=[
    #         'lxmls = lxmls.__main__:cli',
    #     ],
    # ),

    # See: http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are:
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',

        # Indicate who your project is intended for
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        # 'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        # 'Programming Language :: Python :: 3',
        # 'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',

        'Environment :: Other Environment',
    ],
)
