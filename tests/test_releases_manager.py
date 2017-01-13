#!/usr/bin/env python
# -*- coding: utf-8 -*-

import copy
from unittest import TestCase

from fabric.api import env
from mock import call, Mock, patch
from pydiploy.require.releases_manager import (cleanup, deploy_code,
                                               rollback_code, run_tests,
                                               set_current, setup, symlink)


class ReleasesManagerCheck(TestCase):

    """
    test for circus
    """

    def setUp(self):
        self.previous_env = copy.deepcopy(env)
        env.application_name = "appliname"
        env.cfg_shared_files = ["README"]
        env.current_release = "remote_releases_path/4.0"
        env.current_revision = "4.0"
        env.excluded_files = ["fabhappening.jpg"]
        env.extra_pkg_to_install = ["norton-utilities"]
        env.extra_ppa_to_install = ["ppa:/encyclopedia/dramatica"]
        env.extra_source_to_install = [['deb-src http://site.example.com/debian', 'distribution', 'component1', 'component2', 'component3'],]
        env.goals = ['dev', 'test', 'prod']
        env.keep_releases = 3
        env.local_tmp_dir = "/tmp"
        env.local_tmp_root_app = "local_tmp_root_app"
        env.local_tmp_root_app_package = "local_tmp_root_app_package"
        env.previous_release = "3.0"
        env.releases = ["1.0", "2.0", "3.0", "4.0"]
        env.remote_base_package_dir = "remote_base_package_dir"
        env.remote_current_path = "remote_current_path"
        env.remote_current_release = "remote_current_release"
        env.remote_group = "remote_group"
        env.remote_owner = "remote_owner"
        env.remote_project_dir = "remote_project_dir"
        env.remote_releases_path = "remote_releases_path"
        env.remote_repo_specific_folder = "mysubfolder"
        env.remote_repo_url = "remote_repo_url"
        env.remote_shared_path = "remote_shared_path"
        env.root_package_name = "root_package_name"
        env.run_tests_command = 'tox'
        env.tag = "mytag"

    def tearDown(self):
        env.clear()
        env.update(self.previous_env)

    @patch('fabric.api.sudo', return_value=Mock())
    def test_set_current(self, api_sudo):
        set_current()
        self.assertTrue(api_sudo.called)
        self.assertEqual(api_sudo.call_args, call(
            'ln -nfs remote_current_release remote_current_path'))

    @patch('fabric.api.sudo', return_value=Mock())
    @patch('fabric.api.execute', return_value=Mock())
    def test_setup(self, api_execute, api_sudo):
        setup()
        self.assertTrue(api_execute.called)
        self.assertTrue(str(api_execute.call_args).find(
            "function permissions") > 0)
        self.assertTrue(api_sudo.called)
        self.assertEqual(
            api_sudo.call_args_list, [call(
                'mkdir -p remote_project_dir/{releases,shared}'),
                call('mkdir -p remote_shared_path/{config,log}')])

        # extra_symlinks_dirs provided
        env.extra_symlink_dirs = ['symdir']
        setup()
        self.assertTrue(str(api_sudo.call_args_list[4]).find(
            "mkdir -p remote_shared_path/symdir") > 0)

    @patch('fabric.api.sudo', return_value=Mock())
    @patch('pydiploy.prepare.process_releases', return_value=Mock())
    def test_cleanup(self, rel_manager, api_sudo):
        cleanup()
        self.assertTrue(api_sudo.called)
        self.assertEqual(
            api_sudo.call_args, call('rm -rf remote_releases_path/1.0'))

    @patch('pydiploy.require.git.check_tag_exist', return_value=Mock())
    @patch('fabric.api.prompt', return_value=Mock())
    @patch('fabric.api.local', return_value=Mock())
    @patch('fabric.api.require', return_value=Mock())
    @patch('fabric.api.lcd', return_value=Mock())
    @patch('fabric.api.sudo', return_value=Mock())
    @patch('fabric.api.execute', return_value=Mock())
    @patch('fabtools.files.upload_template', return_value=Mock())
    @patch('pydiploy.require.git.archive', return_value="myarchive")
    @patch('fabric.contrib.project.rsync_project', return_value=Mock())
    @patch('fabtools.files.is_file', return_value=None)
    @patch('os.path.exists', return_value=False)
    def test_deploy_code(self, path_exists, is_file, rsync_project, git_archive, upload_template, api_execute, api_sudo, api_lcd, api_require, api_local, api_prompt, tag_exist):
        api_lcd.return_value.__exit__ = Mock()
        api_lcd.return_value.__enter__ = Mock()

        deploy_code()

        self.assertTrue(rsync_project.called)
        self.assertTrue(
            str(rsync_project.call_args).find("'/tmp/appliname-mytag/'") > 0)
        self.assertTrue(str(rsync_project.call_args).find(
            "extra_opts='--links --rsync-path=\"sudo -u remote_owner rsync\"'") > 0)
        self.assertTrue(str(rsync_project.call_args).find("delete=True") > 0)
        self.assertTrue(str(rsync_project.call_args).find(
            "exclude=['fabfile', 'MANIFEST.in', '*.ignore', 'docs', '*.log', 'bin', 'manage.py', '.tox', 'root_package_name/wsgi.py', '*.db', '.gitignore', '.gitattributes', 'root_package_name/settings/dev.py', 'root_package_name/settings/test.py', 'root_package_name/settings/prod.py'") > 0)

        self.assertTrue(git_archive.called)
        self.assertEqual(git_archive.call_args, call(
            'appliname', prefix='appliname-mytag/', tag='mytag', remote='remote_repo_url', specific_folder='mysubfolder'))
        self.assertTrue(upload_template.called)
        self.assertTrue(str(upload_template.call_args_list[0]).find(
            "'/tmp/appliname-mytag/README'") > 0)
        self.assertTrue(str(upload_template.call_args_list[0]).find(
            "'remote_shared_path/config'") > 0)
        self.assertTrue(api_execute.called)
        self.assertTrue(str(api_execute.call_args_list[0]).find(
            "function symlink") > 0)
        self.assertTrue(str(api_execute.call_args_list[1]).find(
            "function set_current") > 0)

        self.assertTrue(api_sudo.called)
        self.assertTrue(str(api_sudo.call_args).find(
            "chown -R remote_owner:remote_group remote_releases_path/") > 0)

        self.assertTrue(api_lcd.called)
        self.assertTrue(str(api_lcd.call_args_list[1]).find('/tmp/appliname-mytag/') > 0)
        #self.assertTrue(str(api_lcd.call_args_list[2]).find('rm myarchive') > 0 )
        #self.assertTrue(str(api_lcd.call_args_list[3]).find('rm -rf /tmp/appliname-mytag') > 0 )
        self.assertTrue(api_local.called)
        self.assertTrue(str(api_local.call_args_list[0]).find('tar xvf myarchive'))
        self.assertTrue(str(api_local.call_args_list[1]).find(env.run_tests_command))

        self.assertTrue(api_require.called)
        self.assertEqual(
            api_require.call_args_list, [call(
                'tag', provided_by=['tag', 'head']),
                call('remote_project_dir', provided_by=['dev', 'test', 'prod'])])

        self.assertTrue(is_file.called)
        self.assertEqual(is_file.call_args, call(
            path='remote_shared_path/config/README', use_sudo=True))

        # extra_symlink_dirs provided
        env.extra_symlink_dirs = ['symdir', ]
        deploy_code()

        del env['tag']
        tag_exist.side_effect = [False,True]
        api_prompt.return_value='4.0'

        deploy_code()
        self.assertTrue(api_prompt.called)
        self.assertEqual(env.tag, '4.0')

        path_exists.return_value=True
        deploy_code()
        self.assertTrue(api_local.called)

    @patch('fabric.api.puts', return_value=Mock())
    @patch('fabric.api.sudo', return_value=Mock())
    @patch('pydiploy.prepare.process_releases', return_value=Mock())
    def test_rollback_code(self, process_rel, api_sudo, api_puts):

        # no old release first deploy with errors so rollback goes on !
        env.releases = []
        rollback_code()
        self.assertTrue(api_sudo.called)
        self.assertEqual(api_sudo.call_args,
                          call('rm remote_current_path && rm -rf remote_current_release'))

        # one release
        env.releases = ["1.0"]
        rollback_code()
        self.assertTrue(api_puts.called)
        self.assertEqual(api_puts.call_args,
                          call('rollback_code : \x1b[32mDone\x1b[0m'))

        env.releases = ["1.0", "2.0", "3.0", "4.0"]
        rollback_code()
        self.assertTrue(api_sudo.called)
        self.assertEqual(api_sudo.call_args,
                         call('rm remote_current_path; ln -s 3.0 remote_current_path && rm -rf remote_releases_path/4.0'))


    @patch('fabric.api.sudo', return_value=Mock())
    def test_symlink(self, api_sudo):
        symlink()
        self.assertTrue(api_sudo.called)
        self.assertEqual(api_sudo.call_args,
                         call('ln -nfs remote_shared_path/config/README remote_current_release/README'))

        # extra_symlink_dirs provided
        env.extra_symlink_dirs = ['symdir', ]
        symlink()
        self.assertTrue(str(api_sudo.call_args_list[4]).find(
            "ln -nfs remote_shared_path/symdir remote_current_release/symdir") > 0)

    @patch('fabric.api.abort', return_value=Mock())
    @patch('fabric.api.local', return_value=Mock())
    @patch('fabric.api.lcd', return_value=Mock())
    def test_run_tests(self, api_lcd, api_local, api_abort):
        api_lcd.return_value.__exit__ = Mock()
        api_lcd.return_value.__enter__ = Mock()
        run_tests()
        env.run_tests_command = 'dtc_les_tests'
        run_tests()
