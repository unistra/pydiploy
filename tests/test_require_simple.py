#!/usr/bin/env python
# -*- coding: utf-8 -*-

import copy
import datetime
from unittest import TestCase
from fabric.api import env
from mock import call, Mock, patch
from pydiploy.require.simple.utils import (app_settings, deploy_environ_file,
                                           extract_settings)


class UtilsCheck(TestCase):

    """
    utils test
    """

    def setUp(self):
        self.previous_env = copy.deepcopy(env)
        env.remote_settings_file = "remote_settings_file"
        env.local_tmp_dir = "tests/data"
        env.goal = "settings"
        env.map_settings = {
            "server_url": "SERVER_URL",
            "default_db_user": "DATABASES['default']['USER']",
            'thanks_arno': ('THANKS_ARNAUD',
                            r'environ.get\(["\']THANKS_ARNAUD[\'"], [\'"](.*)["\']\)')}
        env.local_tmp_root_app_package = "local_tmp_root_app_package"
        env.remote_owner = "owner"
        env.previous_settings_file = "remote_settings_file"
        env.remote_current_release = "remote_current_release"
        env.remote_base_package_dir = "remove_base_package_dir"
        env.local_tmp_root_app = "local_tmp_root_path"

    def tearDown(self):
        env.clear()
        env.update(self.previous_env)

    @patch('fabric.api.get', return_value=Mock())
    def test_extract_settings(self, api_get):

        extract_settings()

        self.assertTrue(api_get.called)
        self.assertEqual(api_get.call_args, call(
            'remote_settings_file', local_path='tests/data'))

        self.assertEqual(env.server_url, '{{ server_url }}')
        self.assertEqual(env.default_db_user, '{{ default_db_user }}')

    @patch('fabtools.files.is_file', return_value=Mock())
    @patch('fabric.api.execute', return_value=Mock())
    @patch('fabric.api.require', return_value=Mock())
    @patch('fabtools.files.upload_template', return_value=Mock())
    def test_app_settings(self, upload_template, api_require, api_execute, is_file):

        # is file true
        app_settings(test1='toto')

        self.assertTrue(is_file.called)
        self.assertEqual(is_file.call_args, call(
            path='remote_settings_file', use_sudo=True))

        self.assertTrue(api_execute.called)
        self.assertTrue(
            str(api_execute.call_args).find('extract_settings') > 0)

        self.assertEqual(env.test1, 'toto')

        self.assertTrue(api_require.called)
        self.assertTrue(str(api_require.call_args).find('server_url') > 0)
        self.assertTrue(str(api_require.call_args).find('default_db_user') > 0)

        self.assertTrue(upload_template.called)
        self.assertTrue(str(upload_template.call_args).find(
            "template_dir='local_tmp_root_app_package/settings'") > 0)
        self.assertTrue(
            str(upload_template.call_args).find("'settings.py'") > 0)
        self.assertTrue(
            str(upload_template.call_args).find("'remote_settings_file'") > 0)
        self.assertTrue(
            str(upload_template.call_args).find("use_jinja=True") > 0)
        self.assertTrue(
            str(upload_template.call_args).find("user='owner'") > 0)

        # is file false
        is_file.return_value = False

        app_settings()

        self.assertTrue(is_file.called)
        self.assertEqual(is_file.call_args, call(
            path='remote_settings_file', use_sudo=True))

    @patch('fabtools.files.upload_template', return_value=Mock())
    def test_deploy_environ_file(self, upload_template):

        deploy_environ_file()
        self.assertTrue(upload_template.called)
