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

import os
import fabtools
import fabric

from string import Template
from fabric.api import env


def sqlite3_pkg(use_sudo=False, user=None):
    """ Installs sqlite3 package and requirements """

    fabtools.require.deb.package('libsqlite3-dev', update=True)
    fabtools.require.python.package(
        'pysqlite', upgrade=True, use_sudo=use_sudo,
        user=user)


def ldap_pkg(use_sudo=False, user=None):
    """ Installs ldap packages and dependencies """

    fabtools.require.deb.package('libldap2-dev', update=True)
    fabtools.require.deb.package('libsasl2-dev', update=True)
    fabtools.require.deb.package('libssl-dev', update=True)
    fabtools.require.python.package(
        'python-ldap', upgrade=True, use_sudo=use_sudo,
        user=user)


def postgres_pkg(update=False):
    """ Installs dependencies for postgresql """

    fabtools.require.deb.packages(['libpq-dev'], update=update)


def install_postgres_server(update=False):
    """ Installs  postgres server on remote """

    # TODO: if deployed app is a django webapp extract settings file to build
    # env vars !!!
    fabtools.require.postgres.server()
    fabtools.require.postgres.user(
        env.default_db_user, env.default_db_password)
    fabtools.require.postgres.database(
        env.default_db_name, owner=env.default_db_user)


def install_oracle_client():
    """
    installs oracle's client for Python oracle_cx.

    needed env vars in fabfile:

    * env.oracle_client_version eg : '11.2.0.2.0'
    * env.oracle_download_url : eg 'http://libshost/lib/oracle_repo/''
    * env.oracle_remote_dir : name of oracle installation directore eg : 'oracle_client'
    * env.oracle_packages : name(s) of zip file(s) for oracle's packages to deploy

    """

    # system libs and goodies installation
    fabtools.require.deb.packages(['libaio-dev', 'unzip'])

    fabtools.require.files.directory(
        path=os.path.join(env.remote_home, env.oracle_remote_dir),
        use_sudo=True,
        owner=env.remote_owner,
        group=env.remote_group,
        mode='750')

    # get oracle's zip file(s) and unzip
    with fabric.api.cd(env.remote_home):
        for package in env.oracle_packages:
            fabric.api.sudo('wget -c %s%s' %
                            (env.oracle_download_url, package))
            fabric.api.sudo('unzip %s -d %s' %
                            (package, env.oracle_remote_dir))
            fabric.api.sudo('rm %s' % os.path.join(env.remote_home, package))

        oracle_dir = 'instantclient_%s' % '_'.join(
            env.oracle_client_version.split('.')[:2])
        oracle_root_path = os.path.join(env.oracle_remote_dir, oracle_dir)
        oracle_full_path = os.path.join(env.remote_home, oracle_root_path)

        with fabric.api.cd(oracle_root_path):
                if not fabtools.files.is_link('libclntsh.so', use_sudo=True):
                    fabric.api.sudo('ln -s libclntsh.so.* libclntsh.so')

        # library configuration
        oracle_conf = Template(
            "# ORACLE CLIENT CONFIGURATION"
            "\nexport ORACLE_HOME=$oracle_dir"
            "\nexport LD_LIBRARY_PATH=$$LD_LIBRARY_PATH:$$ORACLE_HOME"
        )

        fabric.api.sudo('pwd')
        fabric.api.sudo('echo \'%s\' >> .bashrc' %
                        oracle_conf.substitute(oracle_dir=oracle_full_path))
        fabric.api.sudo('source .bashrc')
        fabric.api.sudo(
            'echo %s > /etc/ld.so.conf.d/oracle.conf' % oracle_full_path)
        fabric.api.sudo('ldconfig')


def install_mysql_client(update=False):
    """ Installs dependencies for mysql """
    fabtools.require.deb.packages(['libmysqlclient-dev'], update=update)
