#!/usr/bin/env python
# -*- coding: utf-8 -*-

from unittest import TestCase
from fabric.api import env
from mock import patch, call, Mock
from pydiploy.require.releases_manager import set_current, setup, cleanup, deploy_code, rollback_code, symlink


class ReleasesManagerCheck(TestCase):
    """
    test for circus
    """

    def setUp(self):
        env.remote_current_release = "remote_current_release"
        env.remote_current_path = "remote_current_path"
        env.remote_project_dir = "remote_project_dir"
        env.remote_shared_path = "remote_shared_path"
        env.releases = ["1.0", "2.0", "3.0", "4.0"]
        env.keep_releases = 3
        env.remote_releases_path = "remote_releases_path"
        env.current_revision = "4.0"
        env.previous_release = "3.0"
        env.application_name = "appliname"
        env.tag = "mytag"
        env.remote_repo_url = "remote_repo_url"
        env.root_package_name = "root_package_name"
        env.remote_owner = "remote_owner"
        env.remote_group = "remote_group"
        env.local_tmp_root_app = "local_tmp_root_app"
        env.remote_base_package_dir = "remote_base_package_dir"
        env.local_tmp_root_app_package = "local_tmp_root_app_package"


    def tearDown(self):
        env.clear()


    @patch('fabric.api.sudo', return_value=Mock())
    def test_set_current(self, api_sudo):
        set_current()
        self.assertTrue(api_sudo.called)
        self.assertEqual(api_sudo.call_args, call('ln -nfs remote_current_release remote_current_path'))


    @patch('fabric.api.sudo', return_value=Mock())
    @patch('fabric.api.execute', return_value=Mock())
    def test_setup(self, api_execute, api_sudo):
        setup()
        self.assertTrue(api_execute.called)
        self.assertTrue(str(api_execute.call_args).find(
            "function permissions") > 0)
        self.assertTrue(api_sudo.called)
        self.assertEqual(api_sudo.call_args_list, [call('mkdir -p remote_project_dir/{releases,shared}'),
            call('mkdir -p remote_shared_path/{config,log}')])


    @patch('fabric.api.sudo', return_value=Mock())
    def test_cleanup(self, api_sudo):
        cleanup()
        self.assertTrue(api_sudo.called)
        self.assertEqual(api_sudo.call_args, call('rm -rf remote_releases_path/1.0'))

    @patch('fabric.api.local', return_value=Mock())
    @patch('fabric.api.require', return_value=Mock())
    @patch('fabric.api.lcd', return_value=Mock())
    @patch('fabric.api.sudo', return_value=Mock())
    @patch('fabric.api.execute', return_value=Mock())
    @patch('fabtools.files.upload_template', return_value=Mock())
    @patch('pydiploy.require.git.archive', return_value="myarchive")
    @patch('fabric.contrib.project.rsync_project', return_value=Mock())
    def test_deploy_code(self, rsync_project, git_archive, upload_template, api_execute, api_sudo, api_lcd, api_require, api_local):
        api_lcd.return_value.__exit__ = Mock()
        api_lcd.return_value.__enter__ = Mock()

        deploy_code()

        self.assertTrue(rsync_project.called)
        self.assertTrue(str(rsync_project.call_args).find("'/tmp/appliname-mytag/'") > 0)
        self.assertTrue(str(rsync_project.call_args).find("extra_opts='--rsync-path=\"sudo -u remote_owner rsync\"'") > 0)
        self.assertTrue(str(rsync_project.call_args).find("delete=True") > 0)
        self.assertTrue(str(rsync_project.call_args).find("exclude=['fabfile', 'MANIFEST.in', '*.ignore', 'docs', 'log', 'bin', 'manage.py', 'root_package_name/wsgi.py', '*.db', '.gitignore', 'root_package_name/settings/dev.py', 'root_package_name/settings/test.py', 'root_package_name/settings/prod.py'") > 0)

        self.assertTrue(git_archive.called)
        self.assertEqual(git_archive.call_args, call('appliname', prefix='appliname-mytag/', tag='mytag', remote='remote_repo_url'))

        self.assertTrue(upload_template.called)
        self.assertTrue(str(upload_template.call_args_list[0]).find(
            "'manage.py'") > 0)

        self.assertTrue(str(upload_template.call_args_list[1]).find("'wsgi.py'") > 0)
        self.assertTrue(str(upload_template.call_args_list[1]).find("'remote_base_package_dir/wsgi.py'") > 0)
        self.assertTrue(str(upload_template.call_args_list[1]).find("template_dir='local_tmp_root_app_package'") > 0)
        self.assertTrue(str(upload_template.call_args_list[1]).find("user='remote_owner'") > 0)

        self.assertTrue(api_execute.called)
        self.assertTrue(str(api_execute.call_args_list[0]).find(
            "function symlink") > 0)
        self.assertTrue(str(api_execute.call_args_list[1]).find(
            "function set_current") > 0)

        self.assertTrue(api_sudo.called)
        self.assertTrue(str(api_sudo.call_args).find("chown -R remote_owner:remote_group remote_releases_path/") > 0)

        self.assertTrue(api_lcd.called)
        self.assertEqual(api_lcd.call_args, call('rm myarchive'))

        self.assertTrue(api_local.called)
        self.assertEqual(api_local.call_args, call('tar xvf myarchive'))

        self.assertTrue(api_require.called)
        self.assertEqual(api_require.call_args_list, [call('tag', provided_by=['tag', 'head']),
            call('remote_project_dir', provided_by=['test', 'prod', 'dev'])])


    @patch('fabric.api.sudo', return_value=Mock())
    def test_rollback_code(self, api_sudo):
        rollback_code()
        self.assertTrue(api_sudo.called)
        self.assertEqual(api_sudo.call_args,
            call('rm remote_current_path; ln -s 3.0 remote_current_path && rm -rf remote_releases_path/4.0'))


    @patch('fabric.api.sudo', return_value=Mock())
    def test_symlink(self, api_sudo):
        symlink()
        self.assertTrue(api_sudo.called)
        self.assertEqual(api_sudo.call_args,
            call('ln -nfs remote_shared_path/log remote_current_release/log'))

