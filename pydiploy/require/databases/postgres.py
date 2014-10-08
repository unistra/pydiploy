# -*- coding: utf-8 -*-

"""
postgresql
==========

Required functions for postgresql database

"""

import fabric
import fabtools
from fabric.api import env


def postgres_pkg(update=False):
    """ Installs dependencies for postgresql """

    fabtools.require.deb.packages(['libpq-dev'], update=update)


def install_postgres_server(update=False):
    """ Installs  postgres server on remote """

    # TODO: if deployed app is a django webapp extract settings file to build
    # env vars !!!
    fabtools.require.postgres.server()


def add_postgres_user(name, password, superuser=False, createdb=False,
                        createrole=False, inherit=True, login=True,
                        connection_limit=None, encrypted_password=False,
                        verbose=True):
    """ Installs  postgres server on remote """
    if "verbose_output" in env:
        verbose = env.verbose_output
    if verbose:
        fabric.api.puts('Add %s user for postgresql !' % name)
    if not fabtools.postgres.user_exists(name):
        fabtools.require.postgres.user(name, password, superuser, createdb,
                                       createrole, inherit, login,
                                       connection_limit, encrypted_password)


def add_postgres_database(name, owner, template='template0', encoding='UTF8',
                            locale='fr_FR.UTF-8' ,verbose=True):
    """ Adds  postgresql database on remote """
    if "verbose_output" in env:
        verbose = env.verbose_output
    if verbose:
        fabric.api.puts('Add %s database for owner %s !' % (name, owner))
    if not fabtools.postgres.database_exists(name):
        fabtools.require.postgres.database(name, owner, template, encoding,
                                           locale)
