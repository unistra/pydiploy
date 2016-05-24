#!/usr/bin/env python
# -*- coding: utf-8 -*-

import copy
import re
from unittest import TestCase
from os.path import join
from fabric.api import env
from mock import call, Mock, patch
from pydiploy import version
from pydiploy.prepare import (_get_current_role, build_env,
                              check_req_pydiploy_version, generate_fabfile,
                              init_params, process_releases, tag, test_config,
                              generate_fabfile_simple, generate_fabfile_bottle)


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
        env.remote_static_root = '/var/www/static'
        env.backends = env.roledefs['web']
        env.locale = 'fr_FR.UTF-8'
        env.timezone = 'Europe/Paris'
        env.remote_virtualenv_root = join(env.remote_home, '.virtualenvs')
        env.remote_virtualenv_dir = join(env.remote_virtualenv_root,
                                         env.application_name)
        env.user = 'toto'
        env.remote_python_version = 3.4
        env.keep_releases = 2
        env.short_server_name = 'myapp-dev'

        env.static_folder = '/site_media/'
        env.socket_port = '8001'

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
    def test_build_env_ok(self, api_abort, console_confirm, api_execute, api_run, is_dir, api_prompt):
        build_env()
        self.assertFalse(api_prompt.called)
        self.assertFalse(api_abort.called)
        self.assertFalse(console_confirm.called)
        self.assertFalse(api_execute.called)
        self.assertFalse(api_run.called)
        self.assertFalse(is_dir.called)
        self.assertFalse(api_run.called)
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

    @patch('fabric.api.prompt', return_value="4.0")
    @patch('fabtools.files.is_dir', return_value=True)
    @patch('fabric.api.run', return_value="4.0")
    @patch('fabric.api.execute', return_value=True)
    @patch('fabric.contrib.console.confirm', return_value=Mock())
    @patch('fabric.api.abort', return_value=Mock())
    def test_build_env_no_releases(self, api_abort, console_confirm, api_execute, api_run, is_dir, api_prompt):
        del env['releases']
        build_env()
        self.assertFalse(api_prompt.called)
        self.assertFalse(api_abort.called)
        self.assertFalse(console_confirm.called)
        self.assertTrue(api_execute.called)
        self.assertFalse(api_run.called)
        self.assertFalse(is_dir.called)
        self.assertFalse(api_run.called)


    @patch('fabric.api.prompt', return_value="4.0")
    @patch('fabtools.files.is_dir', return_value=True)
    @patch('fabric.api.run', return_value="4.0")
    @patch('fabric.api.execute', return_value=True)
    @patch('fabric.contrib.console.confirm', return_value=Mock())
    @patch('fabric.api.abort', return_value=Mock())
    def test_build_env_extra_goals(self, api_abort, console_confirm, api_execute, api_run, is_dir, api_prompt):
        env.extra_goals = ['toto']
        build_env()
        self.assertFalse(api_prompt.called)
        self.assertFalse(api_abort.called)
        self.assertFalse(console_confirm.called)
        self.assertFalse(api_execute.called)
        self.assertFalse(api_run.called)
        self.assertFalse(is_dir.called)
        self.assertFalse(api_run.called)
        self.assertEqual(env.goals, ['dev', 'test', 'prod', 'toto'])

    @patch('fabric.api.prompt', return_value="4.0")
    @patch('fabtools.files.is_dir', return_value=True)
    @patch('fabric.api.run', return_value="4.0")
    @patch('fabric.api.execute', return_value=True)
    @patch('fabric.contrib.console.confirm', return_value=Mock())
    @patch('fabric.api.abort', return_value=Mock())
    def test_build_env_verbose(self, api_abort, console_confirm, api_execute, api_run, is_dir, api_prompt):
        env.verbose_output = True
        build_env()
        self.assertFalse(api_prompt.called)
        self.assertFalse(api_abort.called)
        self.assertFalse(console_confirm.called)
        self.assertFalse(api_execute.called)
        self.assertFalse(api_run.called)
        self.assertFalse(is_dir.called)
        self.assertFalse(api_run.called)
        self.assertEqual(env.verbose_output, True)

    @patch('fabric.api.prompt', return_value="4.0")
    @patch('fabtools.files.is_dir', return_value=True)
    @patch('fabric.api.run', return_value="4.0")
    @patch('fabric.api.execute', return_value=True)
    @patch('fabric.contrib.console.confirm', return_value=Mock())
    @patch('fabric.api.abort', return_value=Mock())
    def test_build_env_no_required_packages(self, api_abort, console_confirm, api_execute, api_run, is_dir, api_prompt):
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
        self.assertFalse(api_prompt.called)
        self.assertTrue(api_abort.called)
        self.assertTrue(console_confirm.called)
        self.assertFalse(api_execute.called)
        self.assertFalse(api_run.called)
        self.assertFalse(is_dir.called)
        self.assertFalse(api_run.called)

    @patch('fabric.api.prompt', return_value="4.0")
    @patch('fabtools.files.is_dir', return_value=True)
    @patch('fabric.api.run', return_value="4.0")
    @patch('fabric.api.execute', return_value=True)
    @patch('fabric.contrib.console.confirm', return_value=Mock())
    @patch('fabric.api.abort', return_value=Mock())
    def test_build_env_req_pydiploy_version(self, api_abort, console_confirm, api_execute, api_run, is_dir, api_prompt):
        env.req_pydiploy_version = version.__version__
        build_env()
        self.assertFalse(api_prompt.called)
        self.assertFalse(api_abort.called)
        self.assertFalse(console_confirm.called)
        self.assertFalse(api_execute.called)
        self.assertFalse(api_run.called)
        self.assertFalse(is_dir.called)
        self.assertFalse(api_run.called)

    @patch('fabric.api.prompt', return_value="4.0")
    @patch('fabtools.files.is_dir', return_value=True)
    @patch('fabric.api.run', return_value="4.0")
    @patch('fabric.api.execute', return_value=True)
    @patch('fabric.contrib.console.confirm', return_value=Mock())
    @patch('fabric.api.abort', return_value=Mock())
    def test_build_env_wron_req_pydiploy_version(self, api_abort, console_confirm, api_execute, api_run, is_dir, api_prompt):
        env.req_pydiploy_version = '0.9'
        build_env()
        self.assertFalse(api_prompt.called)
        self.assertFalse(api_abort.called)
        self.assertTrue(console_confirm.called)
        self.assertFalse(api_execute.called)
        self.assertFalse(api_run.called)
        self.assertFalse(is_dir.called)
        self.assertFalse(api_run.called)


    @patch('fabric.api.prompt', return_value="4.0")
    @patch('fabtools.files.is_dir', return_value=True)
    @patch('fabric.api.run', return_value="4.0")
    @patch('fabric.api.execute', return_value=True)
    @patch('fabric.contrib.console.confirm', return_value=Mock())
    @patch('fabric.api.abort', return_value=Mock())
    def test_build_env_application_type(self, api_abort, console_confirm, api_execute, api_run, is_dir, api_prompt):
        env.application_type = 'default'
        build_env()
        self.assertFalse(api_prompt.called)
        self.assertFalse(api_abort.called)
        self.assertFalse(console_confirm.called)
        self.assertFalse(api_execute.called)
        self.assertFalse(api_run.called)
        self.assertFalse(is_dir.called)
        self.assertFalse(api_run.called)


    @patch('fabric.api.prompt', return_value="4.0")
    @patch('fabtools.files.is_dir', return_value=True)
    @patch('fabric.api.run', return_value="4.0")
    @patch('fabric.api.execute', return_value=True)
    @patch('fabric.contrib.console.confirm', return_value=Mock())
    @patch('fabric.api.abort', return_value=Mock())
    def test_build_env_wrong_remote_home(self, api_abort, console_confirm, api_execute, api_run, is_dir, api_prompt):
        env.remote_home = '/'
        build_env()
        self.assertFalse(api_prompt.called)
        self.assertTrue(api_abort.called)
        self.assertFalse(console_confirm.called)
        self.assertFalse(api_execute.called)
        self.assertFalse(api_run.called)
        self.assertFalse(is_dir.called)
        self.assertFalse(api_run.called)
        self.assertEqual(
            api_abort.call_args, call('The remote home cannot be empty or /.'))

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

    def test_generate_fabfile_simple(self):
        generate_fabfile_simple()

    def test_generate_fabfile_bottle(self):
        generate_fabfile_bottle()

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
