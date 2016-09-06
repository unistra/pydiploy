#!/usr/bin/env python
# -*- coding: utf-8 -*-

import copy
from unittest import TestCase

from fabric.api import env
from mock import call, Mock, patch
from pydiploy.require.nginx import (down_site_config, web_static_files,
                                    nginx_pkg, nginx_reload, nginx_restart,
                                    nginx_start, nginx_started, root_web,
                                    set_website_down, set_website_up,
                                    up_site_config, upload_maintenance_page,
                                    web_configuration)


class NginxCheck(TestCase):

    """
    nginx test
    """

    def setUp(self):
        self.previous_env = copy.deepcopy(env)
        env.remote_static_root = "remote_static_root"
        env.local_tmp_dir = 'local_tmp_dir'
        env.server_name = "server_name"
        env.lib_path = "lib_path"
        env.application_name = "application_name"
        env.host_string = 'hosttest'

    def tearDown(self):
        env.clear()
        env.update(self.previous_env)

    @patch('fabtools.require.files.directory', return_value=Mock())
    def test_root_web(self, files_directory):
        root_web()
        self.assertTrue(files_directory.called)
        self.assertEqual(files_directory.call_args, call(
            'remote_static_root', owner='root', use_sudo=True, group='root', mode='755'))

    @patch('fabtools.require.deb.packages', return_value=Mock())
    def test_nginx_pkg(self, deb_packages):
        nginx_pkg()
        self.assertTrue(deb_packages.called)
        self.assertEqual(deb_packages.call_args, call(['nginx'], update=False))

    @patch('fabtools.files.is_dir', return_value=False)
    @patch('fabtools.service.is_running', return_value=False)
    @patch('fabtools.service.start', return_value=Mock())
    def test_nginx_start(self, service_start, is_running, is_systemd):
        # is_running False + Force start to false
        env.nginx_force_start = False
        nginx_start()
        self.assertFalse(service_start.called)
        # is_running False + No force start option
        del env['nginx_force_start']
        nginx_start()
        self.assertFalse(service_start.called)
        # is_running False + Force start to True
        env.nginx_force_start = True
        nginx_start()
        self.assertTrue(service_start.called)

        is_running.return_value = True

        # is_running True + Force start to false
        env.nginx_force_start = False
        nginx_start()
        self.assertTrue(service_start.called)
        # is_running True + No force start option
        del env['nginx_force_start']
        nginx_start()
        self.assertTrue(service_start.called)
        # is_running True + Force start to True
        env.nginx_force_start = True
        nginx_start()
        self.assertTrue(service_start.called)

    @patch('fabtools.files.is_dir', return_value=True)
    @patch('fabric.api.sudo', return_value="inactive")
    @patch('fabtools.systemd.start', return_value=Mock())
    def test_nginx_start_systemd(self, service_start, is_active, is_systemd):
        # is_running False + Force start to false
        env.nginx_force_start = False
        nginx_start()
        self.assertFalse(service_start.called)
        # is_running False + No force start option
        del env['nginx_force_start']
        nginx_start()
        self.assertFalse(service_start.called)
        # is_running False + Force start to True
        env.nginx_force_start = True
        nginx_start()
        self.assertTrue(service_start.called)

        is_active.return_value = "active"

        # is_running True + Force start to false
        env.nginx_force_start = False
        nginx_start()
        self.assertTrue(service_start.called)
        # is_running True + No force start option
        del env['nginx_force_start']
        nginx_start()
        self.assertTrue(service_start.called)
        # is_running True + Force start to True
        env.nginx_force_start = True
        nginx_start()
        self.assertTrue(service_start.called)

    @patch('fabtools.files.is_dir', return_value=False)
    @patch('fabtools.service.is_running', return_value=True)
    @patch('fabtools.service.start', return_value=Mock())
    @patch('fabtools.service.reload', return_value=Mock())
    def test_nginx_reload(self, reload, start, is_running, is_systemd):
        # Nginx run
        nginx_reload()
        self.assertTrue(reload.called)
        self.assertEqual(reload.call_args, call('nginx'))
        self.assertTrue(is_running.called)
        self.assertFalse(start.called)
        # Nginx stopped
        is_running.return_value = False
        reload.called = False
        is_running.called = False
        start.called = False
        nginx_reload()
        self.assertTrue(is_running.called)
        self.assertFalse(reload.called)
        self.assertFalse(start.called)
        # Force reload
        env.nginx_force_start = True
        nginx_reload()
        self.assertTrue(is_running.called)
        self.assertFalse(reload.called)
        self.assertTrue(start.called)
        self.assertEqual(start.call_args, call('nginx'))

    @patch('fabtools.files.is_dir', return_value=True)
    @patch('fabric.api.sudo', return_value="active")
    @patch('fabtools.systemd.start', return_value=Mock())
    @patch('fabtools.systemd.reload', return_value=Mock())
    def test_nginx_reload_systemd(self, reload, start, is_active, is_systemd):
        # Nginx run
        nginx_reload()
        self.assertTrue(reload.called)
        self.assertEqual(reload.call_args, call('nginx'))
        self.assertTrue(is_active.called)
        self.assertFalse(start.called)
        # Nginx stopped
        is_active.return_value = "inactive"
        reload.called = False
        is_active.called = False
        start.called = False
        nginx_reload()
        self.assertTrue(is_active.called)
        self.assertFalse(reload.called)
        self.assertFalse(start.called)
        # Force reload
        env.nginx_force_start = True
        nginx_reload()
        self.assertTrue(is_active.called)
        self.assertFalse(reload.called)
        self.assertTrue(start.called)
        self.assertEqual(start.call_args, call('nginx'))

    @patch('fabtools.files.is_dir', return_value=False)
    @patch('fabtools.service.is_running', return_value=True)
    @patch('fabtools.service.start', return_value=Mock())
    @patch('fabtools.service.restart', return_value=Mock())
    def test_nginx_restart(self, restart, start, is_running, is_systemd):
        # Nginx run
        nginx_restart()
        self.assertTrue(is_running.called)
        self.assertFalse(start.called)
        self.assertTrue(restart.called)
        # Nginx stopped
        is_running.return_value = False
        restart.called = False
        is_running.called = False
        start.called = False
        nginx_restart()
        self.assertFalse(restart.called)
        self.assertTrue(is_running.called)
        self.assertFalse(start.called)
        # Force reload
        env.nginx_force_start = True
        nginx_restart()
        self.assertFalse(restart.called)
        self.assertTrue(is_running.called)
        self.assertTrue(start.called)
        self.assertEqual(start.call_args, call('nginx'))

    @patch('fabtools.files.is_dir', return_value=True)
    @patch('fabric.api.sudo', return_value="active")
    @patch('fabtools.systemd.start', return_value=Mock())
    @patch('fabtools.systemd.restart', return_value=Mock())
    def test_nginx_restart_systemd(self, restart, start, is_active, is_systemd):
        # Nginx run
        nginx_restart()
        self.assertTrue(is_active.called)
        self.assertFalse(start.called)
        self.assertTrue(restart.called)
        # Nginx stopped
        is_active.return_value = "inactive"
        restart.called = False
        is_active.called = False
        start.called = False
        nginx_restart()
        self.assertFalse(restart.called)
        self.assertTrue(is_active.called)
        self.assertFalse(start.called)
        # Force reload
        env.nginx_force_start = True
        nginx_restart()
        self.assertFalse(restart.called)
        self.assertTrue(is_active.called)
        self.assertTrue(start.called)
        self.assertEqual(start.call_args, call('nginx'))

    @patch('fabtools.files.is_dir', return_value=False)
    @patch('fabtools.service.is_running', return_value=True)
    def test_nginx_started(self, is_running, is_systemd):
        res = nginx_started()
        self.assertTrue(is_running.called)
        self.assertEqual(res, True)
        is_running.return_value = False
        res = nginx_started()
        self.assertTrue(is_running.called)
        self.assertEqual(res, False)

    @patch('fabtools.files.is_dir', return_value=True)
    @patch('fabric.api.sudo', return_value="active")
    def test_nginx_started_systemd(self, is_active, is_systemd):
        res = nginx_started()
        self.assertTrue(is_active.called)
        self.assertEqual(res, True)
        is_active.return_value = "inactive"
        res = nginx_started()
        self.assertTrue(is_active.called)
        self.assertEqual(res, False)

    @patch('fabric.contrib.project.rsync_project', return_value=Mock())
    def test_web_static_files(self, rsync_project):
        web_static_files()
        self.assertTrue(rsync_project.called)
        self.assertEqual(rsync_project.call_args,
                         call('remote_static_root/application_name', 'local_tmp_dir/assets/', extra_opts='--rsync-path="sudo rsync" --exclude="maintenance.html"', delete=True, ssh_opts='-t'))

    @patch('pydiploy.require.nginx.up_site_config', return_value=True)
    @patch('pydiploy.require.nginx.down_site_config', return_value=True)
    @patch('fabtools.files.upload_template', return_value=Mock())
    @patch('fabtools.files.is_link', return_value=True)
    @patch('fabric.api.cd', return_value=Mock())
    @patch('fabric.api.sudo', return_value=Mock())
    def test_web_configuration(self, api_sudo, api_cd, is_link, upload_template, up_site_cfg, down_site_cfg):
        api_cd.return_value.__exit__ = Mock()
        api_cd.return_value.__enter__ = Mock()

        web_configuration()

        is_link.return_value = False

        web_configuration()

        self.assertTrue(api_cd.called)
        self.assertEqual(api_cd.call_args,
                         call('/etc/nginx/sites-enabled'))

        self.assertTrue(api_sudo.called)
        self.assertEqual(api_sudo.call_args,
                         call('rm -f default'))

    @patch('fabtools.files.upload_template', return_value=Mock())
    @patch('fabtools.files.is_link', return_value=True)
    @patch('fabric.api.cd', return_value=Mock())
    @patch('fabric.api.sudo', return_value=Mock())
    def test_up_site_conf(self, api_sudo, api_cd, is_link, upload_template):
        api_cd.return_value.__exit__ = Mock()
        api_cd.return_value.__enter__ = Mock()

        up_site_config()

        self.assertTrue(upload_template.called)
        self.assertTrue(
            str(upload_template.call_args).find("'nginx.conf.tpl'") > 0)
        self.assertTrue(str(upload_template.call_args).find(
            "'/etc/nginx/sites-available/server_name.conf'") > 0)
        self.assertTrue(str(upload_template.call_args)
                        .find("template_dir='lib_path/templates'") > 0)

        self.assertTrue(upload_template.is_link)

        is_link.return_value = False

        up_site_config()

        self.assertTrue(api_cd.called)
        self.assertEqual(api_cd.call_args,
                         call('/etc/nginx/sites-enabled'))

        self.assertTrue(api_sudo.called)
        self.assertEqual(api_sudo.call_args, call(
            'ln -s /etc/nginx/sites-available/server_name.conf .'))

    @patch('pydiploy.require.nginx.upload_maintenance_page')
    @patch('fabtools.files.upload_template', return_value=Mock())
    def test_down_site_conf(self, upload_template, maintenance_page):

        down_site_config()

        self.assertTrue(upload_template.called)
        self.assertTrue(maintenance_page.called)
        self.assertTrue(
            str(upload_template.call_args).find("'nginx_down.conf.tpl'") > 0)
        self.assertTrue(str(upload_template.call_args).find(
            "'/etc/nginx/sites-available/server_name_down.conf'") > 0)
        self.assertTrue(str(upload_template.call_args)
                        .find("template_dir='lib_path/templates'") > 0)

    @patch('fabtools.files.upload_template', return_value=Mock())
    @patch('fabtools.files.is_link', return_value=True)
    @patch('fabric.api.cd', return_value=Mock())
    @patch('fabric.api.sudo', return_value=Mock())
    def test_up_site_conf(self, api_sudo, api_cd, is_link, upload_template):

        api_cd.return_value.__exit__ = Mock()
        api_cd.return_value.__enter__ = Mock()

        up_site_config()

        self.assertTrue(upload_template.called)
        self.assertTrue(
            str(upload_template.call_args).find("'nginx.conf.tpl'") > 0)
        self.assertTrue(str(upload_template.call_args).find(
            "'/etc/nginx/sites-available/server_name.conf'") > 0)
        self.assertTrue(str(upload_template.call_args)
                        .find("template_dir='lib_path/templates'") > 0)

        is_link.return_value = False
        up_site_config()

        self.assertTrue(api_cd.called)
        self.assertEqual(api_cd.call_args,
                         call('/etc/nginx/sites-enabled'))

        self.assertTrue(api_sudo.called)
        self.assertEqual(api_sudo.call_args, call(
            'ln -s /etc/nginx/sites-available/server_name.conf .'))

    @patch('pydiploy.require.nginx.nginx_reload', return_value=Mock())
    @patch('fabric.api.sudo', return_value=Mock())
    @patch('fabric.api.cd', return_value=Mock())
    @patch('fabtools.files.is_link', return_value=True)
    @patch('pydiploy.require.nginx.up_site_config', return_value=Mock())
    @patch('fabtools.files.is_file', return_value=True)
    def test_set_website_up(self, is_file, up_site_config, is_link, api_cd, api_sudo, nginx_reload):

        api_cd.return_value.__exit__ = Mock()
        api_cd.return_value.__enter__ = Mock()
        set_website_up()

        self.assertTrue(api_cd.called)
        self.assertEqual(api_cd.call_args,
                         call('/etc/nginx/sites-enabled'))
        self.assertTrue(api_sudo.called)
        self.assertEqual(api_sudo.call_args, call(
            'rm -f server_name_down.conf'))

        # no up config file
        is_file.return_value = False
        set_website_up()

        self.assertTrue(up_site_config.called)

        # no symlink
        is_link.return_value = False
        set_website_up()

        self.assertTrue(api_cd.called)
        self.assertEqual(api_cd.call_args,
                         call('/etc/nginx/sites-enabled'))

        self.assertTrue(api_sudo.called)
        self.assertEqual(api_sudo.call_args, call(
            'ln -s /etc/nginx/sites-available/server_name.conf .'))

    @patch('pydiploy.require.nginx.nginx_reload', return_value=Mock())
    @patch('fabric.api.sudo', return_value=Mock())
    @patch('fabric.api.cd', return_value=Mock())
    @patch('fabtools.files.is_link', return_value=True)
    @patch('pydiploy.require.nginx.down_site_config', return_value=Mock())
    @patch('fabtools.files.is_file', return_value=True)
    def test_set_website_down(self, is_file, down_site_config, is_link, api_cd, api_sudo, nginx_reload):

        api_cd.return_value.__exit__ = Mock()
        api_cd.return_value.__enter__ = Mock()
        set_website_down()

        self.assertTrue(api_cd.called)
        self.assertEqual(api_cd.call_args,
                         call('/etc/nginx/sites-enabled'))
        self.assertTrue(api_sudo.called)
        self.assertEqual(api_sudo.call_args, call(
            'rm -f server_name.conf'))

        # no up config file
        is_file.return_value = False
        set_website_down()

        self.assertTrue(down_site_config.called)

        # no symlink
        is_link.return_value = False
        set_website_down()

        self.assertTrue(api_cd.called)
        self.assertEqual(api_cd.call_args,
                         call('/etc/nginx/sites-enabled'))

        self.assertTrue(api_sudo.called)
        self.assertEqual(api_sudo.call_args, call(
            'ln -s /etc/nginx/sites-available/server_name_down.conf .'))

    @patch('fabtools.files.upload_template', return_value=Mock())
    def test_upload_maintenance_page(self, upload_template):

        upload_maintenance_page()
        self.assertTrue(upload_template.called)
        self.assertTrue(str(upload_template.call_args)
                        .find("maintenance.html.tpl") > 0)
        self.assertTrue(str(upload_template.call_args)
                        .find("remote_static_root/application_name/maintenance.html") > 0)
        self.assertTrue(str(upload_template.call_args)
                        .find("template_dir='lib_path/templates'") > 0)

        env.maintenance_text = "ééééééééééééééééééé"
        env.maintenance_title = "ààààààà"
        upload_maintenance_page()
