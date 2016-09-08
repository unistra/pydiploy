#!/usr/bin/env python
# -*- coding: utf-8 -*-

import copy
from unittest import TestCase

from fabric.api import env
from mock import call, Mock, patch
from pydiploy.django import (application_packages, custom_manage_command,
                             deploy_backend, deploy_frontend, dump_database,
                             install_oracle_client, install_postgres_server,
                             install_sap_client, post_install_backend,
                             post_install_frontend, pre_install_backend,
                             pre_install_frontend, reload_backend,
                             reload_frontend, rollback, set_app_down,
                             set_app_up, wrap_deploy)


class ReleasesManagerCheck(TestCase):

    """
    test for circus
    """

    def setUp(self):
        self.previous_env = copy.deepcopy(env)
        env.remote_python_version = 2.7
        env.locale = 'fr_FR.UTF-8'

    def tearDown(self):
        env.clear()
        env.update(self.previous_env)

    @patch('fabric.api.abort', return_value=Mock())
    @patch('fabric.api.execute', return_value=Mock())
    def test_wrap_deploy(self, api_execute, api_abort):
        wrap_deploy()



    @patch('fabtools.require.deb.packages', return_value=Mock())
    @patch('fabric.api.execute', return_value=Mock())
    def test_application_packages(self, api_execute, deb_packages):
        application_packages()
        self.assertTrue(deb_packages.called)
        self.assertEqual(
            deb_packages.call_args, call(['gettext'], update=False))
        self.assertTrue(api_execute.called)
        self.assertTrue(
            str(api_execute.call_args_list[0]).find('call(<function python_pkg') == 0)

        # env.remote_python_version >= 3
        env.remote_python_version = 3
        application_packages()
        self.assertTrue(api_execute.called)
        self.assertTrue(
            str(api_execute.call_args_list[1]).find('call(<function check_python3_install') == 0)

        # test extra pppa
        env.extra_ppa_to_install = "ppa:myppa/ppafromhell"
        application_packages()
        self.assertTrue(api_execute.called)
        self.assertTrue(
            str(api_execute.call_args_list[5]).find('call(<function install_extra_ppa') == 0)

        # test extra pkg
        env.extra_pkg_to_install = "pkgfromhell"
        application_packages()
        self.assertTrue(api_execute.called)
        self.assertTrue(
            str(api_execute.call_args_list[9]).find('call(<function install_extra_packages') == 0)

        # test extra debian source
        env.extra_source_to_install = [["cool debian source", "cool", "cool", "cool"],]
        application_packages()
        self.assertTrue(api_execute.called)
        self.assertTrue(
            str(api_execute.call_args_list[13]).find('call(<function install_extra_source') == 0)


    @patch('fabric.api.execute', return_value=Mock())
    def test_pre_install_backend(self, api_execute):
        pre_install_backend()
        self.assertTrue(api_execute.called)
        self.assertTrue(
            str(api_execute.call_args_list[0]).find('call(<function add_user') == 0)
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
    def test_deploy_backend(self, api_execute):
        deploy_backend()
        self.assertTrue(api_execute.called)
        self.assertTrue(str(api_execute.call_args_list[0]).find(
            'call(<function setup') == 0)
        self.assertTrue(str(api_execute.call_args_list[1]).find(
            'call(<function deploy_code') == 0)
        self.assertTrue(str(api_execute.call_args_list[2]).find(
            'call(<function deploy_manage_file') == 0)
        self.assertTrue(str(api_execute.call_args_list[3]).find(
            'call(<function deploy_wsgi_file') == 0)
        self.assertTrue(str(api_execute.call_args_list[4]).find(
            'call(<function application_dependencies') == 0)
        self.assertTrue(str(api_execute.call_args_list[5]).find(
            'call(<function app_settings') == 0)
        self.assertTrue(str(api_execute.call_args_list[6]).find(
            'call(<function django_prepare') == 0)
        self.assertTrue(
            str(api_execute.call_args_list[7]).find('call(<function permissions') == 0)
        self.assertTrue(
            str(api_execute.call_args_list[8]).find('call(<function app_reload') == 0)
        self.assertTrue(
            str(api_execute.call_args_list[9]).find('call(<function cleanup') == 0)

        #api_execute.return_value = Mock(side_effect=Exception(SystemExit))
        try:
            api_execute.side_effect = Exception(SystemExit)
            deploy_backend()
        except:
            pass
        self.assertTrue(api_execute.called)

    @patch('fabric.api.execute', return_value=Mock())
    def test_deploy_frontend(self, api_execute):
        deploy_frontend()
        self.assertTrue(api_execute.called)
        self.assertTrue(str(api_execute.call_args_list[0]).find(
            'call(<function web_static_files') == 0)

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
            'call(<function web_configuration') == 0)
        self.assertTrue(str(api_execute.call_args_list[1]).find(
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

    @patch('pydiploy.require.nginx.set_website_down', return_value=Mock())
    @patch('fabric.api.execute', return_value=Mock())
    def test_set_app_down(self, api_execute, website_down):

        set_app_down()

    @patch('pydiploy.require.nginx.set_website_up', return_value=Mock())
    @patch('fabric.api.execute', return_value=Mock())
    def test_set_app_up(self, api_execute, website_down):

        set_app_up()

    @patch('fabric.api.execute', return_value=Mock())
    def test_custom_manage_command(self, api_execute):

        custom_manage_command('toto')

    @patch('fabric.api.abort', return_value=Mock())
    @patch('fabric.api.execute', return_value=Mock())
    def test_install_postgres_server(self, api_execute, api_abort):

        # no parameters provided env.default_db_* no present
        install_postgres_server()
        self.assertTrue(api_abort.called)

        # no parameters provided env.default_db_* present
        env.default_db_user = "foo"
        env.default_db_name = "foo"
        env.default_db_password = "bar"
        install_postgres_server()
        self.assertTrue(api_execute.called)
        self.assertTrue(str(api_execute.call_args_list[0]).find(
            'call(<function install_postgres_server') == 0)
        self.assertTrue(str(api_execute.call_args_list[1]).find(
            'call(<function add_postgres_user') == 0)
        self.assertTrue(str(api_execute.call_args_list[2]).find(
            'call(<function add_postgres_database') == 0)

        # parameters provided
        install_postgres_server(user='foo', dbname='foo', password='bar')

    @patch('fabric.api.execute', return_value=Mock())
    def test_install_oracle_client(self, api_execute):

        install_oracle_client()
        self.assertTrue(api_execute.called)
        self.assertTrue(str(api_execute.call_args_list[0]).find(
            'call(<function install_oracle_client') == 0)

    @patch('fabric.api.execute', return_value=Mock())
    def test_install_sap_client(self, api_execute):

        install_sap_client()
        self.assertTrue(api_execute.called)
        self.assertTrue(str(api_execute.call_args_list[0]).find(
            'call(<function install_sap_client') == 0)
