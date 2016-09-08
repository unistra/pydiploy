#!/usr/bin/env python
# -*- coding: utf-8 -*-

import copy
from unittest import TestCase

from fabric.api import env
from mock import call, Mock, patch
from pydiploy.simple import (wrap_deploy, application_packages,
                             deploy_backend, post_install_backend,
                             pre_install_backend, rollback)


class ReleasesManagerCheck(TestCase):

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
        env.extra_source_to_install = {("cool debian source"),}
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
            str(api_execute.call_args_list[5]).find('call(<function virtualenv') == 0)

    @patch('fabric.api.execute', return_value=Mock())
    def test_deploy_backend(self, api_execute):
        deploy_backend()
        self.assertTrue(api_execute.called)
        self.assertTrue(str(api_execute.call_args_list[0]).find(
            'call(<function setup') == 0)
        self.assertTrue(str(api_execute.call_args_list[1]).find(
            'call(<function deploy_code') == 0)
        self.assertTrue(str(api_execute.call_args_list[2]).find(
            'call(<function application_dependencies') == 0)
        self.assertTrue(str(api_execute.call_args_list[3]).find(
            'call(<function app_settings') == 0)
        self.assertTrue(str(api_execute.call_args_list[4]).find(
            'call(<function deploy_environ_file') == 0)
        self.assertTrue(
            str(api_execute.call_args_list[5]).find('call(<function permissions') == 0)
        self.assertTrue(
            str(api_execute.call_args_list[6]).find('call(<function cleanup') == 0)

        #api_execute.return_value = Mock(side_effect=Exception(SystemExit))
        try:
            api_execute.side_effect = Exception(SystemExit)
            deploy_backend()
        except:
            pass
        self.assertTrue(api_execute.called)
        print str(api_execute.call_args_list)

    @patch('fabric.api.execute', return_value=Mock())
    def test_rollback(self, api_execute):
        rollback()
        self.assertTrue(api_execute.called)
        self.assertTrue(str(api_execute.call_args_list[0]).find(
            'call(<function rollback_code') == 0)

    @patch('fabric.api.execute', return_value=Mock())
    def test_post_install_backend(self, api_execute):
        """ post install backend do nothing currently """
        post_install_backend()
        self.assertFalse(api_execute.called)
