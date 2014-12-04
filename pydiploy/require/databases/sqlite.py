# -*- coding: utf-8 -*-

"""
sqlite
======

Required functions for sqlite database

"""

import fabtools
from pydiploy.decorators import do_verbose


@do_verbose
def sqlite3_pkg(use_sudo=False, user=None):
    """ Installs sqlite3 package and requirements """

    fabtools.require.deb.package('libsqlite3-dev', update=True)
    fabtools.require.python.package(
        'pysqlite', upgrade=True, use_sudo=use_sudo,
        user=user)
