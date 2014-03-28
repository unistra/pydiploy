# -*- coding: utf-8 -*-

"""
Database
========

Requires function to install database client for Python ::

    sqlite3
    oracle
    postgresql
    mysql

"""

import fabtools


def sqlite3_pkg(use_sudo=False, user=None):
    """
    Require python client for sqlite3

    Installing in a virtualenv ::

        from fabtools.python import virtualenv
        from pydiploy import require

        with virtualenv('/path/to/virtualenv'):
            fabtools.require.database.sqlite3()

    Installing for wide system ::

        from pydiploy import require

        fabtools.require.database.sqlite3(use_sudo=True)
    """

    fabtools.require.deb.package('libsqlite3-dev', update=True)
    fabtools.require.python.package('pysqlite', upgrade=True, use_sudo=use_sudo,
                           user=user)


def ldap_pkg(use_sudo=False, user=None):
    """
    Installs ldap packages and dependencies
    """

    fabtools.require.deb.package('libldap2-dev', update=True)
    fabtools.require.deb.package('libsasl2-dev', update=True)
    fabtools.require.deb.package('libssl-dev', update=True)
    fabtools.require.python.package('python-ldap', upgrade=True, use_sudo=use_sudo,
                           user=user)


def postgres_pkg(update=False):
    """
    Installs dependencies for postgresql
    """
    fabtools.require.deb.packages(['libpq-dev'], update=update)
