#!/usr/bin/env python
# -*- coding: utf-8 -*-

import copy
from unittest import TestCase

from fabric.api import env
from mock import call, Mock, patch
from pydiploy.require.databases.ldap import ldap_pkg
from pydiploy.require.databases.mongodb import install_mongodb
from pydiploy.require.databases.mysql import (add_mysql_database,
                                              add_mysql_user,
                                              install_mysql_client,
                                              install_mysql_server)
from pydiploy.require.databases.oracle import (get_oracle_jdk_version,
                                               install_oracle_client,
                                               install_oracle_jdk)
from pydiploy.require.databases.postgres import (add_postgres_database,
                                                 add_postgres_user,
                                                 install_postgres_server,
                                                 postgres_pkg)
from pydiploy.require.databases.sqlite import sqlite3_pkg
from pydiploy.require.databases.sap import install_sap_client


class LdapCheck(TestCase):

    """
    test database
    """

    def setUp(self):

        self.previous_env = copy.deepcopy(env)

    def tearDown(self):
        env.clear()
        env.update(self.previous_env)

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


class Sqlite3Check(TestCase):

    """
    test database
    """

    def setUp(self):

        self.previous_env = copy.deepcopy(env)

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


class PostgresCheck(TestCase):

    """
    test database
    """

    def setUp(self):

        self.previous_env = copy.deepcopy(env)
        env.verbose_output = True
        env.locale = 'fr_FR.UTF-8'

    def tearDown(self):
        env.clear()
        env.update(self.previous_env)

    @patch("fabtools.require.deb.packages", return_value=Mock())
    def test_postgres_pkg(self, deb_packages):
        postgres_pkg()

        self.assertTrue(deb_packages.called)
        self.assertEqual(
            deb_packages.call_args, call(['libpq-dev'], update=False))

    @patch("fabtools.require.postgres.server", return_value=Mock())
    def test_install_postgres_server(self, postgres_server):

        install_postgres_server()
        self.assertTrue(postgres_server.called)

    @patch("fabtools.postgres.user_exists", return_value=False)
    @patch("fabtools.require.postgres.user", return_value=Mock())
    def test_add_postgres_user(self, postgres_user, postgres_user_exist):

        add_postgres_user(name='bill', password='g@t3s')
        self.assertTrue(postgres_user.called)
        self.assertEqual(
            postgres_user.call_args, call('bill', 'g@t3s', False, False, False, True, True, None, False))

        # verbose_output = false
        env.verbose_output = False
        add_postgres_user(name='bill', password='g@t3s')
        self.assertTrue(postgres_user.called)

        # user exists
        postgres_user_exist.return_value = True
        add_postgres_user(name='bill', password='g@t3s')


    @patch("fabtools.postgres.database_exists", return_value=False)
    @patch("fabtools.require.postgres.database", return_value=Mock())
    def test_add_postgres_database(self, postgres_database, postgres_db_exists):

        add_postgres_database('db', 'dbowner')
        self.assertTrue(postgres_db_exists)
        self.assertTrue(postgres_database.called)

        # user exists
        postgres_db_exists.return_value = True
        add_postgres_database('db', 'dbowner')
        self.assertTrue(postgres_db_exists)
        self.assertEqual(postgres_db_exists.return_value, True)


class MysqlCheck(TestCase):

    """
    test database
    """

    def setUp(self):

        self.previous_env = copy.deepcopy(env)

    def tearDown(self):
        env.clear()
        env.update(self.previous_env)

    @patch("fabtools.require.deb.packages", return_value=Mock())
    def test_install_mysql_client(self, deb_packages):

        install_mysql_client()

        self.assertTrue(deb_packages.called)
        self.assertEqual(deb_packages.call_args,
                         call(['libmysqlclient-dev'], update=False))

    @patch("fabtools.require.mysql.server", return_value=Mock())
    def test_install_mysql_server(self, mysql_server):

        install_mysql_server()

        self.assertTrue(mysql_server.called)

    @patch("fabtools.mysql.user_exists", return_value=False)
    @patch("fabtools.mysql.create_user", return_value=Mock())
    def test_add_mysql_user(self, mysql_user, mysql_user_exists):

        add_mysql_user('bill', 'g@t3s')

        self.assertTrue(mysql_user_exists.called)
        self.assertTrue(mysql_user.called)

        mysql_user_exists.return_value = True

        add_mysql_user('steve', 'j0b$')
        self.assertTrue(mysql_user_exists.called)

    @patch("fabtools.mysql.database_exists", return_value=False)
    @patch("fabtools.mysql.create_database", return_value=Mock())
    def test_add_mysql_database(self, db_mysql, db_exists):

        add_mysql_database('bill', 'bill')

        self.assertTrue(db_exists.called)
        self.assertTrue(db_mysql.called)

        db_exists.return_value = True

        add_mysql_database('steve', 'steve')
        self.assertTrue(db_exists.called)


class OracleCheck(TestCase):

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
        env.locale = 'fr_FR.UTF-8'

    def tearDown(self):
        env.clear()
        env.update(self.previous_env)

    @patch('fabric.api.abort', return_value=Mock())
    @patch("fabtools.files.is_link", return_value=False)
    @patch("fabric.api.sudo", return_value=Mock())
    @patch("fabric.api.cd", return_value=Mock())
    @patch("fabtools.require.files.directory", return_value=Mock())
    @patch("fabtools.require.deb.packages", return_value=Mock())
    def test_install_oracle_client(self, deb_packages, files_directory,
                                   api_cd, api_sudo, files_is_link, api_abort):

        api_cd.return_value.__exit__ = Mock()
        api_cd.return_value.__enter__ = Mock()

        install_oracle_client()

        self.assertTrue(deb_packages.called)
        self.assertEqual(deb_packages.call_args,
                         call(['libaio-dev', 'unzip']))

        self.assertTrue(files_directory.called)
        self.assertEqual(files_directory.call_args,
                         call(path='/home/django/oracle_client', use_sudo=True, owner='django',
                              group='di', mode='750'))

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

        del env['oracle_client_version']
        install_oracle_client()
        self.assertTrue(api_abort.called)

    @patch("fabtools.oracle_jdk.install_from_oracle_site", return_value=Mock())
    def test_install_oracle_jdk(self, oracle_jdk_install):

        install_oracle_jdk()

        self.assertTrue(oracle_jdk_install.called)

        install_oracle_jdk(version='7u25-b15')

        self.assertTrue(oracle_jdk_install.called)
        self.assertEqual(
            oracle_jdk_install.call_args, call(version='7u25-b15'))

    @patch("fabtools.oracle_jdk.version", return_value=Mock())
    def test_oracle_jdk_version(self, jdk_version):

        get_oracle_jdk_version()

        self.assertTrue(jdk_version.called)


class MongoCheck(TestCase):

    """
    test database
    """

    def setUp(self):

        self.previous_env = copy.deepcopy(env)

    def tearDown(self):
        env.clear()
        env.update(self.previous_env)

    @patch("fabtools.require.deb.package", return_value=Mock())
    @patch('fabtools.require.deb.uptodate_index', return_value=Mock())
    @patch("fabric.api.sudo", return_value=Mock())
    @patch("fabtools.require.deb.source", return_value=Mock())
    @patch("pydiploy.require.system.package_installed", return_value=True)
    def test_install_mongodb(self, is_package_installed, deb_source, api_sudo,
                             uptodate_index, deb_package):

        # nothing to do
        install_mongodb()
        self.assertTrue(is_package_installed.called)

        # install mongodb package
        is_package_installed.return_value = False
        install_mongodb()
        self.assertTrue(is_package_installed.called)

        self.assertTrue(deb_source.called)
        self.assertEqual(deb_source.call_args,
                         call('mongodb',
                              'http://downloads-distro.mongodb.org/repo/ubuntu-upstart',
                              'dist', '10gen'))
        self.assertTrue(api_sudo.called)
        self.assertEqual(api_sudo.call_args,
                         call('apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 7F0CEB10'))
        self.assertTrue(uptodate_index.called)
        self.assertTrue(deb_package.called)
        self.assertEqual(deb_package.call_args,
                         call('mongodb-10gen'))


class SAPCheck(TestCase):

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
        env.sap_download_url = 'http://librepo.net/lib/sap/'
        env.sap_packages = ['rfcsdk_64.tar.gz']
        env.locale = 'fr_FR.UTF-8'

    def tearDown(self):
        env.clear()
        env.update(self.previous_env)

    @patch('fabric.api.abort', return_value=Mock())
    @patch("fabtools.files.is_link", return_value=False)
    @patch("fabric.api.sudo", return_value=Mock())
    @patch("fabric.api.cd", return_value=Mock())
    @patch("fabtools.require.files.directory", return_value=Mock())
    @patch("fabtools.require.deb.packages", return_value=Mock())
    def test_install_sap_client(self, deb_packages, files_directory,
                                api_cd, api_sudo, files_is_link, api_abort):

        api_cd.return_value.__exit__ = Mock()
        api_cd.return_value.__enter__ = Mock()

        install_sap_client()

        self.assertTrue(deb_packages.called)
        self.assertEqual(deb_packages.call_args,
                         call(['libstdc++5']))

        self.assertTrue(files_directory.called)
        self.assertEqual(files_directory.call_args,
                         call(path='/usr/sap', use_sudo=True, mode='755'))

        self.assertTrue(api_cd.called)
        self.assertEqual(api_cd.call_args_list,
                         [call('/usr/sap'), call('/lib')])

        self.assertTrue(api_sudo.called)
        self.assertEqual(api_sudo.call_args_list, [
            call('wget -c http://librepo.net/lib/sap/rfcsdk_64.tar.gz'),
            call('tar xvf rfcsdk_64.tar.gz'),
            call('chmod -R 755 rfcsdk'),
            call('rm rfcsdk_64.tar.gz'),
            call('ln -s /usr/sap/rfcsdk/lib/librfccm.so .')
        ])

        del env['sap_download_url']
        install_sap_client()
        self.assertTrue(api_abort.called)
