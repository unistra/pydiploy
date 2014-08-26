#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup
from setuptools import find_packages

with open('README.rst') as readme:
    long_description = readme.read()

with open('requirements.txt') as requirements:
    lines = requirements.readlines()
    libraries = [lib for lib in lines if not lib.startswith('-')]
    dependency_links = [link.split()[1] for link in lines if
                        link.startswith('-f')]

setup(
    name='pydiploy',
    version='1.0.2.1',
    author='di-dip-unistra',
    author_email='di-dip@unistra.fr',
    maintainer='di-dip-unistra',
    maintainer_email='di-dip@unistra.fr',
    url='https://github.com/unistra/pydiploy',
    license='PSF',
    description='A tool to deploy applications, and automate processing with fabric',
    long_description=long_description,
    packages=find_packages(),
    include_package_data=True,
    download_url='http://pypi.python.org/pypi/pydiploy',
    install_requires=libraries,
    dependency_links=dependency_links,
    keywords=['deploy', 'fabric', 'automation'],
    entry_points={},
    classifiers=(
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7'
    )
)
