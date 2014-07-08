#!/usr/bin/env python
# -*- coding: utf-8 -*-

from unittest import TestCase
from fabric.api import env
from mock import patch, call, Mock
from pydiploy.django import application_packages, \
pre_install_frontend,pre_install_backend, deploy, rollback, post_install_backend, post_install_frontend


class ReleasesManagerCheck(TestCase):
    """
    test for circus
    """

    def setUp(self):
        env.remote_python_version = 2.7

    def tearDown(self):
        env.clear()


    @patch('fabtools.require.deb.packages', return_value=Mock())
    @patch('fabric.api.execute', return_value=Mock())
    def test_application_packages(self, api_execute, deb_packages):
        application_packages()
        self.assertTrue(deb_packages.called)
        self.assertEqual(deb_packages.call_args, call(['gettext'], update=False))
        self.assertTrue(api_execute.called)
        self.assertTrue(str(api_execute.call_args_list[0]).find('call(<function ldap_pkg') == 0)
        self.assertTrue(str(api_execute.call_args_list[1]).find('call(<function postgres_pkg') == 0)
        self.assertTrue(str(api_execute.call_args_list[2]).find('call(<function python_pkg') == 0)


    @patch('fabric.api.execute', return_value=Mock())
    def pre_install_backend(self, api_execute):
        pre_install_backend()
        self.assertTrue(api_execute.called)
        self.assertTrue(str(api_execute.call_args_list[1]).find('call(<function django_user') == 0)
        self.assertTrue(str(api_execute.call_args_list[2]).find('call(<function set_locale') == 0)
        self.assertTrue(str(api_execute.call_args_list[3]).find('call(<function set_timezone') == 0)
        self.assertTrue(str(api_execute.call_args_list[4]).find('call(<function update_pkg_index') == 0)
        self.assertTrue(str(api_execute.call_args_list[5]).find('call(<function application_packages') == 0)
        self.assertTrue(str(api_execute.call_args_list[6]).find('call(<function circus_pkg') == 0)
        self.assertTrue(str(api_execute.call_args_list[7]).find('call(<function virtualenv') == 0)
        self.assertTrue(str(api_execute.call_args_list[8]).find('call(<function upstart') == 0)



    @patch('fabric.api.execute', return_value=Mock())
    def pre_install_frontend(self, api_execute):
        pre_install_frontend()
        self.assertTrue(api_execute.called)
        self.assertTrue(str(api_execute.call_args_list[0]).find('call(<function root_web') == 0)
        self.assertTrue(str(api_execute.call_args_list[1]).find('call(<function update_pkg_index') == 0)
        self.assertTrue(str(api_execute.call_args_list[2]).find('call(<function nginx_pkg') == 0)


    @patch('fabric.api.execute', return_value=Mock())
    def test_deploy(self, api_execute):
        deploy()
        self.assertTrue(api_execute.called)
        self.assertTrue(str(api_execute.call_args_list[0]).find('call(<function setup') == 0)
        self.assertTrue(str(api_execute.call_args_list[1]).find('call(<function deploy_code') == 0)
        self.assertTrue(str(api_execute.call_args_list[2]).find('call(<function application_dependencies') == 0)
        self.assertTrue(str(api_execute.call_args_list[3]).find('call(<function app_settings') == 0)
        self.assertTrue(str(api_execute.call_args_list[4]).find('call(<function django_prepare') == 0)
        self.assertTrue(str(api_execute.call_args_list[5]).find('call(<function permissions') == 0)
        self.assertTrue(str(api_execute.call_args_list[6]).find('call(<function app_reload') == 0)
        self.assertTrue(str(api_execute.call_args_list[7]).find('call(<function cleanup') == 0)


    @patch('fabric.api.execute', return_value=Mock())
    def test_rollback(self, api_execute):
        rollback()
        self.assertTrue(api_execute.called)
        self.assertTrue(str(api_execute.call_args_list[0]).find('call(<function rollback_code') == 0)
        self.assertTrue(str(api_execute.call_args_list[1]).find('call(<function app_reload') == 0)



    @patch('fabric.api.execute', return_value=Mock())
    def test_post_install_frontend(self, api_execute):
        post_install_frontend()
        self.assertTrue(api_execute.called)
        self.assertTrue(str(api_execute.call_args_list[0]).find('call(<function web_static_files') == 0)
        self.assertTrue(str(api_execute.call_args_list[1]).find('call(<function web_configuration') == 0)
        self.assertTrue(str(api_execute.call_args_list[2]).find('call(<function nginx_restart') == 0)

    @patch('fabric.api.execute', return_value=Mock())
    def test_post_install_backend(self, api_execute):
        post_install_backend()
        self.assertTrue(api_execute.called)
        self.assertTrue(str(api_execute.call_args_list[0]).find('call(<function app_circus_conf') == 0)
        self.assertTrue(str(api_execute.call_args_list[1]).find('call(<function app_reload') == 0)
