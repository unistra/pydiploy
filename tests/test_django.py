#!/usr/bin/env python
# -*- coding: utf-8 -*-

import copy
from unittest import TestCase

from fabric.api import env
from mock import call, Mock, patch
from pydiploy.django import (application_packages, deploy, dump_database,
                             post_install_backend, post_install_frontend,
                             pre_install_backend, pre_install_frontend,
                             reload_backend, reload_frontend, rollback)


class ReleasesManagerCheck(TestCase):

    """
    test for circus
    """

    def setUp(self):
        self.previous_env = copy.deepcopy(env)
        env.remote_python_version = 2.7

    def tearDown(self):
        env.clear()
        env.update(self.previous_env)

    @patch('fabtools.require.deb.packages', return_value=Mock())
    @patch('fabric.api.execute', return_value=Mock())
    def test_application_packages(self, api_execute, deb_packages):
        application_packages()
        self.assertTrue(deb_packages.called)
        self.assertEqual(
            deb_packages.call_args, call(['gettext'], update=False))
        self.assertTrue(api_execute.called)
        self.assertTrue(
            str(api_execute.call_args_list[0]).find('call(<function ldap_pkg') == 0)
        self.assertTrue(
            str(api_execute.call_args_list[1]).find('call(<function postgres_pkg') == 0)
        self.assertTrue(
            str(api_execute.call_args_list[2]).find('call(<function python_pkg') == 0)

        # env.remote_python_version >= 3
        env.remote_python_version = 3
        application_packages()
        self.assertTrue(api_execute.called)
        self.assertTrue(
            str(api_execute.call_args_list[5]).find('call(<function check_python3_install') == 0)

        # test extra pppa
        env.extra_ppa_to_install = "ppa:myppa/ppafromhell"
        application_packages()
        self.assertTrue(api_execute.called)
        self.assertTrue(
            str(api_execute.call_args_list[11]).find('call(<function install_extra_ppa') == 0)

        # test extra pkg
        env.extra_pkg_to_install = "pkgfromhell"
        application_packages()
        self.assertTrue(api_execute.called)
        self.assertTrue(
            str(api_execute.call_args_list[17]).find('call(<function install_extra_packages') == 0)

    @patch('fabric.api.execute', return_value=Mock())
    def test_pre_install_backend(self, api_execute):
        pre_install_backend()
        self.assertTrue(api_execute.called)
        self.assertTrue(
            str(api_execute.call_args_list[0]).find('call(<function django_user') == 0)
        self.assertTrue(
            str(api_execute.call_args_list[1]).find('call(<function set_locale') == 0)
        self.assertTrue(str(api_execute.call_args_list[2]).find(
            'call(<function set_timezone') == 0)
        self.assertTrue(str(api_execute.call_args_list[3]).find(
            'call(<function update_pkg_index') == 0)
        self.assertTrue(str(api_execute.call_args_list[4]).find(
            'call(<function application_packages') == 0)
        self.assertTrue(
            str(api_execute.call_args_list[5]).find('call(<function circus_pkg') == 0)
        self.assertTrue(
            str(api_execute.call_args_list[6]).find('call(<function virtualenv') == 0)
        self.assertTrue(
            str(api_execute.call_args_list[7]).find('call(<function upstart') == 0)

    @patch('fabric.api.execute', return_value=Mock())
    def test_pre_install_frontend(self, api_execute):
        pre_install_frontend()
        self.assertTrue(api_execute.called)
        self.assertTrue(
            str(api_execute.call_args_list[0]).find('call(<function root_web') == 0)
        self.assertTrue(str(api_execute.call_args_list[1]).find(
            'call(<function update_pkg_index') == 0)
        self.assertTrue(
            str(api_execute.call_args_list[2]).find('call(<function nginx_pkg') == 0)

    @patch('fabric.api.execute', return_value=Mock())
    def test_deploy(self, api_execute):
        deploy()
        self.assertTrue(api_execute.called)
        self.assertTrue(
            str(api_execute.call_args_list[0]).find('call(<function setup') == 0)
        self.assertTrue(
            str(api_execute.call_args_list[1]).find('call(<function deploy_code') == 0)
        self.assertTrue(str(api_execute.call_args_list[2]).find(
            'call(<function application_dependencies') == 0)
        self.assertTrue(str(api_execute.call_args_list[3]).find(
            'call(<function app_settings') == 0)
        self.assertTrue(str(api_execute.call_args_list[4]).find(
            'call(<function django_prepare') == 0)
        self.assertTrue(
            str(api_execute.call_args_list[5]).find('call(<function permissions') == 0)
        self.assertTrue(
            str(api_execute.call_args_list[6]).find('call(<function app_reload') == 0)
        self.assertTrue(
            str(api_execute.call_args_list[7]).find('call(<function cleanup') == 0)

    @patch('fabric.api.execute', return_value=Mock())
    def test_rollback(self, api_execute):
        rollback()
        self.assertTrue(api_execute.called)
        self.assertTrue(str(api_execute.call_args_list[0]).find(
            'call(<function rollback_code') == 0)
        self.assertTrue(
            str(api_execute.call_args_list[1]).find('call(<function app_reload') == 0)

    @patch('fabric.api.execute', return_value=Mock())
    def test_post_install_frontend(self, api_execute):
        post_install_frontend()
        self.assertTrue(api_execute.called)
        self.assertTrue(str(api_execute.call_args_list[0]).find(
            'call(<function web_static_files') == 0)
        self.assertTrue(str(api_execute.call_args_list[1]).find(
            'call(<function web_configuration') == 0)
        self.assertTrue(str(api_execute.call_args_list[2]).find(
            'call(<function nginx_restart') == 0)

    @patch('fabric.api.execute', return_value=Mock())
    def test_post_install_backend(self, api_execute):
        post_install_backend()
        self.assertTrue(api_execute.called)
        self.assertTrue(str(api_execute.call_args_list[0]).find(
            'call(<function app_circus_conf') == 0)
        self.assertTrue(
            str(api_execute.call_args_list[1]).find('call(<function app_reload') == 0)

    @patch('fabric.api.execute', return_value=Mock())
    def test_dump_database(self, api_execute):
        dump_database()
        self.assertTrue(api_execute.called)
        self.assertTrue(str(api_execute.call_args_list[0]).find(
            'call(<function django_dump_database') == 0)

    @patch('fabric.api.execute', return_value=Mock())
    def test_reload_frontend(self, api_execute):
        reload_frontend()
        self.assertTrue(api_execute.called)
        self.assertTrue(str(api_execute.call_args_list[0]).find(
            'call(<function nginx_reload') == 0)

    @patch('fabric.api.execute', return_value=Mock())
    def test_reload_backend(self, api_execute):
        reload_backend()
        self.assertTrue(api_execute.called)
        self.assertTrue(str(api_execute.call_args_list[0]).find(
            'call(<function app_reload') == 0)
