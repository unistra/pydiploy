#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


setup(
    name="pydiploy",

    version='0.2',
    packages=find_packages(
        'src', exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    package_dir={'': 'src'},

    install_requires=[
        'fabric',
    ],
    dependency_links=[
        'http://repodipory.u-strasbg.fr/lib/python'
    ],


    author='dip',
    author_email='di-dip@unistra.fr',
    description='Déploiement automatisé, gestion de l\'environnement de développement et gestion de la prodution'
    'pour une application Python',
    keywords="deploy development automatic production",
    url='http://git.u-strasbg.fr/git/pydiploy',


)
