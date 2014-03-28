#!/usr/bin/env python
# -*- coding: utf-8 -*-

from unittest import TestCase
from fabric.api import env
from mock import patch, call, Mock
from pydiploy.prepare import tag, build_env


class PrepareCheck(TestCase):
    """
    test for circus
    """

    def setUp(self):
        env.remote_home = "remote_home"
        env.server_name = "server_name"
        env.local_tmp_dir = "local_tmp_dir"
        env.application_name = "application_name"
        env.root_package_name = "root_package_name"
        env.goal = "goal"
        env.releases = ["1.0", "2.0", "3.0", "4.0"]
        env.tag = "4.0"


    def tearDown(self):
        env.clear()


    def test_tag(self):
        tag("4.0")
        self.assertEqual(env.tag, "4.0")



    @patch('fabric.api.prompt', return_value="4.0")
    @patch('fabtools.files.is_dir', return_value=True)
    @patch('fabric.api.run', return_value="4.0")
    def test_build_env(self, api_run, is_dir, api_prompt):
        build_env()
        self.assertFalse(api_prompt.called)
        del env['tag']
        build_env()
        self.assertTrue(api_prompt.called)
        # test env var
        self.assertEqual(env.remote_project_dir, "remote_home/server_name")
        self.assertEqual(env.local_tmp_root_app, "local_tmp_dir/application_name-4.0")
        self.assertEqual(env.local_tmp_root_app_package, "local_tmp_dir/application_name-4.0/root_package_name")
        self.assertEqual(env.remote_current_path, "remote_home/server_name/current")
        self.assertEqual(env.remote_releases_path, "remote_home/server_name/releases")
        self.assertEqual(env.remote_shared_path, "remote_home/server_name/shared")
        self.assertEqual(env.remote_base_package_dir, "remote_home/server_name/current/root_package_name")
        self.assertEqual(env.remote_settings_dir, "remote_home/server_name/current/root_package_name/settings")
        self.assertEqual(env.remote_settings_file, "remote_home/server_name/current/root_package_name/settings/goal.py")
        self.assertEqual(env.lib_path, "pydiploy")

        #test if no env release
        del env['releases']
        build_env()

        self.assertTrue(is_dir.called)

        self.assertTrue(api_run.called)
        self.assertEqual(api_run.call_args, call('ls -x remote_home/server_name/releases'))

        # with 1 release
        self.assertEqual(env.releases, ['4.0'])
        self.assertEqual(env.remote_project_dir, "remote_home/server_name")
        self.assertEqual(env.current_revision, "4.0")
        self.assertEqual(env.current_release, "remote_home/server_name/releases/4.0")

        #with 2 release
        del env['releases']
        api_run.return_value = "4.0 3.0"
        build_env()

        self.assertEqual(env.releases, ['3.0', '4.0'])
        self.assertEqual(env.remote_project_dir, "remote_home/server_name")
        self.assertEqual(env.current_revision, "4.0")
        self.assertEqual(env.current_release, "remote_home/server_name/releases/4.0")
        self.assertEqual(env.previous_revision, "3.0")
        self.assertEqual(env.previous_release, "remote_home/server_name/releases/3.0")




