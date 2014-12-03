# -*- coding: utf-8 -*-

"""
Mysql
=====

Requires functions for mysql database

"""


import fabtools
from pydiploy.decorators import do_verbose


@do_verbose
def install_mysql_client(update=False):
    """ Installs dependencies for mysql """
    fabtools.require.deb.packages(['libmysqlclient-dev'], update=update)


@do_verbose
def install_mysql_server(version=None, password=None):
    """ Installs mysql server """
    fabtools.require.mysql.server(version=version, password=password)


@do_verbose
def add_mysql_user(name, password, host='localhost', **kwargs):
    """ Adds mysql user """
    if not fabtools.mysql.user_exists(name):
        fabtools.mysql.create_user(
            name, password=password, host=host, **kwargs)


@do_verbose
def add_mysql_database(name, owner=None, owner_host='localhost',
                       charset='utf8', collate='utf8_general_ci', **kwargs):
    """ Adds mysql database """
    if not fabtools.mysql.database_exists(name):
        fabtools.mysql.create_database(name, owner=owner, charset=charset,
                                       collate=collate, **kwargs)
