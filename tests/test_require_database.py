#!/usr/bin/env python
# -*- coding: utf-8 -*-

from unittest import TestCase
from fabric.api import env
from mock import patch, call, Mock
from pydiploy.require.database import sqlite3_pkg, ldap_pkg, postgres_pkg


class DatabaseCheck(TestCase):

    """
    test database
    """

    def tearDown(self):
        env.clear()

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
        self.assertEqual(deb_packages.call_args, call(['libpq-dev'], update=False))
         