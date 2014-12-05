#!/usr/bin/env python
# -*- coding: utf-8 -*-

import copy
import re
from unittest import TestCase

from fabric.api import env
from mock import call, Mock, patch
from pydiploy import version
from pydiploy.prepare import (_get_current_role, build_env,
                              check_req_pydiploy_version, generate_fabfile,
                              init_params, process_releases, tag, test_config)


class PrepareCheck(TestCase):

    """
    test for circus
    """

    def setUp(self):
        self.previous_env = copy.deepcopy(env)
        env.application_name = "application_name"
        env.goal = "goal"
        env.host = '192.168.1.2'
        env.host_string = ""
        env.host_string = env.host
        env.local_tmp_dir = "local_tmp_dir"
        env.output_prefix = ""
        env.previous_release = "3.0"
        env.releases = ["1.0", "2.0", "3.0", "4.0"]
        env.remote_base_package_dir = "remote_base_package_dir"
        env.remote_current_path = "remote_current_path"
        env.remote_current_release = "remote_current_release"
        env.remote_group = "remote_group"
        env.remote_home = "remote_home"
        env.remote_owner = "remote_owner"
        env.remote_project_dir = "remote_home/server_name"
        env.remote_releases_path = "remote_home/server_name/releases"
        env.remote_repo_url = "remote_repo_url"
        env.remote_shared_path = "remote_shared_path"
        env.roledefs = {'web': ['192.168.1.2'], 'lb': ['192.168.1.3'], }
        env.root_package_name = "root_package_name"
        env.server_name = "server_name"
        env.tag = "4.0"

    def tearDown(self):
        env.clear()
        env.update(self.previous_env)

    @patch('fabric.api.abort', return_value=Mock())
    @patch('pydiploy.require.git.collect_tags', return_value=[''])
    @patch('pydiploy.require.git.collect_branches', return_value=['master','4.0'])
    @patch('pydiploy.require.git.check_tag_exist', return_value=Mock())
    def test_tag(self, tag_exist, collect_branches, collect_tags, api_abort):

        del env['tag']

        # test tag called after goal eg: fab test tag:master deploy
        env.pydiploy_version = 1664
        tag('fail')
        self.assertTrue(api_abort.called)

        # check tag unknown
        del env['pydiploy_version']
        tag_exist.return_value = False
        tag('fail')
        self.assertTrue(api_abort.called)

        tag_exist.return_value = True
        tag('master')
        self.assertEqual(env.tag, 'master')

        tag('4.0')
        self.assertEqual(env.tag, '4.0')


    @patch('fabric.api.prompt', return_value="4.0")
    @patch('fabtools.files.is_dir', return_value=True)
    @patch('fabric.api.run', return_value="4.0")
    @patch('fabric.api.execute', return_value=True)
    @patch('fabric.contrib.console.confirm', return_value=Mock())
    @patch('fabric.api.abort', return_value=Mock())
    def test_build_env(self, api_abort, console_confirm, api_execute, api_run, is_dir, api_prompt):

        build_env()
        self.assertFalse(api_prompt.called)
        del env['tag']
        # self.assertTrue(api_execute.called)
        build_env()
        # test env var
        self.assertEqual(env.remote_project_dir, "remote_home/server_name")
        self.assertEqual(
            env.local_tmp_root_app, "local_tmp_dir/application_name-4.0")
        self.assertEqual(env.local_tmp_root_app_package,
                         "local_tmp_dir/application_name-4.0/root_package_name")
        self.assertEqual(
            env.remote_current_path, "remote_home/server_name/current")
        self.assertEqual(
            env.remote_releases_path, "remote_home/server_name/releases")
        self.assertEqual(
            env.remote_shared_path, "remote_home/server_name/shared")
        self.assertEqual(env.remote_base_package_dir,
                         "remote_home/server_name/current/root_package_name")
        self.assertEqual(env.remote_settings_dir,
                         "remote_home/server_name/current/root_package_name/settings")
        self.assertEqual(env.remote_settings_file,
                         "remote_home/server_name/current/root_package_name/settings/goal.py")
        self.assertTrue(re.match("^.*pydiploy$", env.lib_path))
        self.assertEqual(env.goals, ['dev', 'test', 'prod'])

        # no releases
        del env['releases']
        build_env()

        # test env.extra_goals
        env.extra_goals = ['toto']
        build_env()
        self.assertEqual(env.goals, ['dev', 'test', 'prod', 'toto'])

        # test misconfiguration and abort
        api_execute.return_value = False
        console_confirm.return_value = False
        build_env()
        self.assertTrue(console_confirm.called)
        self.assertTrue(api_abort.called)
        self.assertEqual(
            api_abort.call_args, call('Aborting at user request.'))

        # test all required params are set
        env.root_package_name = 'foo'
        env.server_name = 'foo'
        env.remote_static_root = 'foo'
        env.goal = 'foo'
        env.backends = 'foo'
        env.locale = 'foo'
        env.remote_virtualenv_dir = 'foo'
        env.user = 'foo'
        env.roledefs = 'foo'
        env.remote_python_version = 'foo'
        env.keep_releases = 'foo'
        env.remote_home = 'foo'
        env.remote_owner = 'foo'
        env.timezone = 'foo'
        env.application_name = 'foo'
        env.remote_repo_url = 'foo'
        env.short_server_name = 'foo'
        env.remote_virtualenv_root = 'foo'
        env.remote_group = 'foo'
        env.static_folder = 'foo'
        env.socket_port = 'foo'
        env.local_tmp_dir = 'foo'
        env.roledefs = {'web': ['192.168.1.21'], 'lb': ['1164-web2'], }
        build_env()

        # test env.verbose set
        env.verbose_output = True
        build_env()

        # test env.verbose_output not set
        del env['dest_path']
        del env['verbose_output']
        build_env()

        # test optional params not set
        del env['dest_path']
        del env['extra_goals']
        build_env()

        # test no required params are set
        env.root_package_name = ''
        env.server_name = ''
        env.remote_static_root = ''
        env.goal = ''
        env.backends = ''
        env.locale = ''
        env.remote_virtualenv_dir = ''
        env.user = ''
        env.roledefs = ''
        env.remote_python_version = ''
        env.keep_releases = ''
        env.remote_home = ''
        env.remote_owner = ''
        env.timezone = ''
        env.application_name = ''
        env.remote_repo_url = ''
        env.short_server_name = ''
        env.remote_virtualenv_root = ''
        env.remote_group = ''
        env.static_folder = ''
        env.socket_port = ''
        env.local_tmp_dir = ''
        build_env()

        # check req_pydiploy_version
        env.req_pydiploy_version = '0.9'
        build_env()

        env.req_pydiploy_version = '1.2'
        build_env()

        # good version
        env.req_pydiploy_version = version.__version__
        build_env()


    @patch('fabric.api.puts', return_value=Mock())
    def test_config(self, api_puts):
        test_config()
        self.assertTrue(api_puts.called)

        # no config check
        env.no_config_test = True
        test_config()

    def test_get_current_role(self):
        _get_current_role()

    def test_check_req_pydiploy_version(self):
        check_req_pydiploy_version()

    def test_generate_fabfile(self):
        generate_fabfile()

    @patch('fabtools.files.is_dir', return_value=True)
    @patch('fabric.api.run', return_value="4.0")
    def test_process_releases(self, api_run, is_dir):

        del env['releases']
        process_releases()

        self.assertTrue(is_dir.called)
        self.assertTrue(api_run.called)
        self.assertEqual(api_run.call_args, call(
            'ls -x remote_home/server_name/releases'))

        #with 1 release
        api_run.return_value = "4.0"
        process_releases()

        self.assertEqual(env.releases, ['4.0'])
        self.assertEqual(env.remote_project_dir, "remote_home/server_name")
        self.assertEqual(env.current_revision, "4.0")
        self.assertEqual(
            env.current_release, "remote_home/server_name/releases/4.0")

        # with 2 release
        del env['releases']
        api_run.return_value = "4.0 3.0"
        process_releases()

        self.assertEqual(env.releases, ['3.0', '4.0'])
        self.assertEqual(env.remote_project_dir, "remote_home/server_name")
        self.assertEqual(env.current_revision, "4.0")
        self.assertEqual(
            env.current_release, "remote_home/server_name/releases/4.0")
        self.assertEqual(env.previous_revision, "3.0")
        self.assertEqual(
            env.previous_release, "remote_home/server_name/releases/3.0")
