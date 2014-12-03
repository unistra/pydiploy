# -*- coding: utf-8 -*-

"""
postgresql
==========

Required functions for postgresql database

"""

import fabric
import fabtools
from fabric.api import env
from pydiploy.decorators import do_verbose


@do_verbose
def postgres_pkg(update=False):
    """ Installs dependencies for postgresql """

    fabtools.require.deb.packages(['libpq-dev'], update=update)


@do_verbose
def install_postgres_server(update=False):
    """ Installs  postgres server on remote """

    # TODO: if deployed app is a django webapp extract settings file to build
    # env vars !!!
    fabtools.require.postgres.server()


@do_verbose
def add_postgres_user(name, password, superuser=False, createdb=False,
                      createrole=False, inherit=True, login=True,
                      connection_limit=None, encrypted_password=False,
                      verbose=True):
    """ Installs  postgres server on remote """
    if "verbose_output" in env:
        verbose = env.verbose_output
        msg = ''

    if not fabtools.postgres.user_exists(name):
        fabtools.require.postgres.user(name, password, superuser, createdb,
                                       createrole, inherit, login,
                                       connection_limit, encrypted_password)
        msg = 'Add %s user for postgresql !' % fabric.colors.green(name)
    else:
        msg = 'User %s already exists !' % fabric.colors.red(name)

    if verbose:
        fabric.api.puts(msg)


@do_verbose
def add_postgres_database(name, owner, template='template0', encoding='UTF8',
                          locale='fr_FR.UTF-8', verbose=True):
    """ Adds  postgresql database on remote """
    if "verbose_output" in env:
        verbose = env.verbose_output
        msg = ''

    if not fabtools.postgres.database_exists(name):
        fabtools.require.postgres.database(name, owner, template, encoding,
                                           locale)
        msg = 'Add %s database for owner %s !' % (
            fabric.colors.green(name), fabric.colors.green(owner))
    else:
        msg = 'Database %s for owner %s already exists !' % (
            fabric.colors.red(name), fabric.colors.red(owner))

    if verbose:
        fabric.api.puts(msg)
