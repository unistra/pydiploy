#!/usr/bin/env python
# -*- coding: utf-8 -*-

import copy

from unittest import TestCase
from fabric.api import env
from mock import patch, call, Mock
from pydiploy.require.database import sqlite3_pkg, ldap_pkg, postgres_pkg, \
    install_postgres_server, install_mysql_client, install_oracle_client


class DatabaseCheck(TestCase):

    """
    test database
    """

    def setUp(self):

        self.previous_env = copy.deepcopy(env)

        env.default_db_user = 'bill'
        env.default_db_password = 'g@t3s'
        env.default_db_name = 'kr0s0ft'
        env.remote_home = '/home/django'
        env.remote_owner = 'django'
        env.remote_group = 'di'
        env.oracle_client_version = '11.2'
        env.oracle_download_url = 'http://librepo.net/lib/oracle/'
        env.oracle_remote_dir = 'oracle_client'
        env.oracle_packages = ['instantclient-basic-linux-x86-64-11.2.0.2.0.zip',
                               'instantclient-sdk-linux-x86-64-11.2.0.2.0.zip',
                               'instantclient-sqlplus-linux-x86-64-11.2.0.2.0.zip']

    def tearDown(self):
        env.clear()
        env.update(self.previous_env)

    @patch("fabtools.require.deb.package", return_value=Mock())
    @patch("fabtools.require.python.package", return_value=Mock())
    def test_sqlite3_pkg(self, python_package, deb_package):
        sqlite3_pkg()

        self.assertTrue(python_package.called)
        self.assertEqual(python_package.call_args,
                         call('pysqlite', upgrade=True, use_sudo=False, user=None))

        self.assertTrue(deb_package.called)
        self.assertEqual(deb_package.call_args,
                         call('libsqlite3-dev', update=True))

    @patch("fabtools.require.deb.package", return_value=Mock())
    @patch("fabtools.require.python.package", return_value=Mock())
    def test_ldap_pkg(self, python_package, deb_package):
        ldap_pkg()

        self.assertTrue(python_package.called)
        self.assertEqual(python_package.call_args,
                         call('python-ldap', upgrade=True, use_sudo=False, user=None))

        self.assertTrue(deb_package.called)
        self.assertEqual(deb_package.call_args_list,
                         [call('libldap2-dev', update=True), call('libsasl2-dev', update=True), call('libssl-dev', update=True)])

    @patch("fabtools.require.deb.packages", return_value=Mock())
    def test_postgres_pkg(self, deb_packages):
        postgres_pkg()

        self.assertTrue(deb_packages.called)
        self.assertEqual(
            deb_packages.call_args, call(['libpq-dev'], update=False))

    @patch("fabtools.require.postgres.database", return_value=Mock())
    @patch("fabtools.require.postgres.user", return_value=Mock())
    @patch("fabtools.require.postgres.server", return_value=Mock())
    def test_install_postgres_server(self, postgres_server, postgres_user, postgres_database):

        install_postgres_server()

        self.assertTrue(postgres_server.called)
        self.assertTrue(postgres_user.called)
        self.assertEqual(
            postgres_user.call_args, call('bill', 'g@t3s'))
        self.assertTrue(postgres_database.called)

    @patch("fabtools.require.deb.packages", return_value=Mock())
    def test_install_mysql_client(self, deb_packages):

        install_mysql_client()

        self.assertTrue(deb_packages.called)
        self.assertEqual(deb_packages.call_args,
                         call(['libmysqlclient-dev'], update=False))

    @patch("fabtools.files.is_link", return_value=False)
    @patch("fabric.api.sudo", return_value=Mock())
    @patch("fabric.api.cd", return_value=Mock())
    @patch("fabtools.require.files.directory", return_value=Mock())
    @patch("fabtools.require.deb.packages", return_value=Mock())
    def test_install_oracle_client(self, deb_packages, files_directory, api_cd, api_sudo, files_is_link):

        api_cd.return_value.__exit__ = Mock()
        api_cd.return_value.__enter__ = Mock()

        install_oracle_client()

        self.assertTrue(deb_packages.called)
        self.assertEqual(deb_packages.call_args,
                         call(['libaio-dev', 'unzip']))

        self.assertTrue(files_directory.called)
        self.assertEqual(files_directory.call_args,
                         call(path='/home/django/oracle_client', use_sudo=True, owner='django', group='di', mode='750'))

        self.assertTrue(api_cd.called)
        self.assertEqual(api_cd.call_args_list,
                         [call('/home/django'), call('oracle_client/instantclient_11_2')])

        self.assertTrue(api_sudo.called)
        self.assertEqual(api_sudo.call_args_list,
                         [call('wget -c http://librepo.net/lib/oracle/instantclient-basic-linux-x86-64-11.2.0.2.0.zip'),
                          call(
                             'unzip instantclient-basic-linux-x86-64-11.2.0.2.0.zip -d oracle_client'),
                          call(
                             'rm /home/django/instantclient-basic-linux-x86-64-11.2.0.2.0.zip'),
                          call(
                             'wget -c http://librepo.net/lib/oracle/instantclient-sdk-linux-x86-64-11.2.0.2.0.zip'),
                          call(
                             'unzip instantclient-sdk-linux-x86-64-11.2.0.2.0.zip -d oracle_client'),
                          call(
                             'rm /home/django/instantclient-sdk-linux-x86-64-11.2.0.2.0.zip'),
                          call(
                             'wget -c http://librepo.net/lib/oracle/instantclient-sqlplus-linux-x86-64-11.2.0.2.0.zip'),
                          call(
                             'unzip instantclient-sqlplus-linux-x86-64-11.2.0.2.0.zip -d oracle_client'),
                          call(
                             'rm /home/django/instantclient-sqlplus-linux-x86-64-11.2.0.2.0.zip'),
                          call('ln -s libclntsh.so.* libclntsh.so'),
                          call('pwd'),
                          call(
                             "echo '# ORACLE CLIENT CONFIGURATION\nexport ORACLE_HOME=/home/django/oracle_client/instantclient_11_2\nexport LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$ORACLE_HOME' >> .bashrc"),
                          call('source .bashrc'),
                          call(
                             'echo /home/django/oracle_client/instantclient_11_2 > /etc/ld.so.conf.d/oracle.conf'),
                          call('ldconfig')])
