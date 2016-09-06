#!/usr/bin/env python
# -*- coding: utf-8 -*-

import copy
from unittest import TestCase

from fabric.api import env
from mock import call, Mock, patch
from pydiploy.require.system import (check_python3_install, add_group,
                                     add_user, install_extra_packages,
                                     install_extra_ppa, install_extra_source,
                                     package_installed, permissions, set_locale,
                                     set_timezone, update_pkg_index)


class SystemCheck(TestCase):

    """
    test for System
    """

    def setUp(self):
        self.previous_env = copy.deepcopy(env)
        env.remote_group = "remote_group"
        env.remote_owner = "remote_owner"
        env.locale = "FR_fr"
        env.server_name = "server_name"
        env.timezone = "mytimezone"
        env.remote_project_dir = "remote_project_dir"

    def tearDown(self):
        env.clear()
        env.update(self.previous_env)

    @patch('fabtools.require.group', return_value=Mock())
    @patch('fabtools.require.user', return_value=Mock())
    @patch('fabtools.require.sudoer', return_value=Mock())
    def test_add_user(self, require_group, require_user, require_sudoer):
        add_user(commands='mycommand')

        self.assertTrue(require_group.called)
        self.assertEqual(require_group.call_args, call(
            '%remote_group', passwd=False, commands='mycommand', operators='remote_owner,root'))

        self.assertTrue(require_user.called)
        self.assertEqual(require_user.call_args, call(
            'remote_owner', create_group=True, shell='/bin/bash', group='remote_group', create_home=True))

        self.assertTrue(require_sudoer.called)
        self.assertEqual(require_sudoer.call_args, call('remote_group'))

    @patch('fabtools.require.group', return_value=Mock())
    def test_add_group(self, require_group):
        add_group("mygroup")
        self.assertTrue(require_group.called)
        self.assertEqual(require_group.call_args, call('mygroup'))

    @patch('fabtools.require.deb.uptodate_index', return_value=Mock())
    def test_update_pkg_index(self, uptodate_index):
        update_pkg_index()
        self.assertTrue(uptodate_index.called)
        self.assertEqual(uptodate_index.call_args, call(max_age={'day': 1}))

    @patch('fabric.api.run', return_value="FR_fr")
    @patch('fabric.api.sudo', return_value=Mock())
    def test_set_locale(self, api_sudo, api_run):
        set_locale()

        self.assertTrue(api_run.called)
        self.assertFalse(api_sudo.called)

        api_run.return_value = "otherlocale"

        set_locale()

        self.assertTrue(api_run.called)
        self.assertTrue(api_sudo.called)
        self.assertEqual(api_sudo.call_args_list, [
                         call('locale-gen FR_fr'), call('/usr/sbin/update-locale LANG=FR_fr')])

    @patch('fabtools.files.is_link', return_value=False)
    @patch('fabtools.system.distrib_id', return_value='Notsupported')
    @patch('fabric.api.sudo', return_value=Mock())
    def test_set_timezone(self, api_sudo, distrib_id, is_link):
        set_timezone()
        # test error
        self.assertTrue(distrib_id.called)
        self.assertFalse(api_sudo.called)

        # test if it works
        distrib_id.return_value = 'Ubuntu'
        set_timezone()
        self.assertTrue(distrib_id.called)
        self.assertTrue(api_sudo.called)

        self.assertEqual(api_sudo.call_args, call(
            'cp -f /usr/share/zoneinfo/mytimezone /etc/localtime'))

    @patch('fabtools.files.is_link', return_value=True)
    @patch('fabtools.system.distrib_id', return_value='Notsupported')
    @patch('fabric.api.sudo', return_value=Mock())
    def test_set_timezone_link(self, api_sudo, distrib_id, is_link):
        set_timezone()
        # test error
        self.assertTrue(distrib_id.called)
        self.assertFalse(api_sudo.called)

        # test if it works
        distrib_id.return_value = 'Ubuntu'
        set_timezone()
        self.assertTrue(distrib_id.called)
        self.assertTrue(api_sudo.called)

        self.assertEqual(api_sudo.call_args, call(
            'ln -sf /usr/share/zoneinfo/mytimezone /etc/localtime'))

    @patch('fabric.api.sudo', return_value=Mock())
    def test_permissions(self, api_sudo):
        permissions()
        self.assertTrue(api_sudo.called)
        self.assertEqual(
            api_sudo.call_args, call('chmod -R g+w remote_project_dir'))

    @patch('fabric.api.settings', return_value=Mock())
    @patch('fabric.api.sudo', return_value=Mock())
    def test_package_installed(self, api_sudo, api_settings):

        api_settings.return_value.__exit__ = Mock()
        api_settings.return_value.__enter__ = Mock()

        package_installed("package")
        self.assertTrue(api_sudo.called)
        self.assertEqual(
            api_sudo.call_args, call('dpkg-query -l "package" | grep -q ^.i'))

    @patch('fabtools.require.deb.packages', return_value=Mock())
    def test_install_extra_packages(self, deb_pkgs):

        install_extra_packages('ponysays')
        self.assertTrue(deb_pkgs.called)
        self.assertEqual(deb_pkgs.call_args, call('ponysays', update=False))

    @patch('fabtools.require.deb.ppa', return_value=Mock())
    def test_install_extra_ppa(self, deb_ppa):

        install_extra_ppa(['ppa:myppa/ppa', ])
        self.assertTrue(deb_ppa.called)
        self.assertEqual(deb_ppa.call_args, call('ppa:myppa/ppa'))

    @patch('fabtools.require.deb.source', return_value=Mock())
    def test_install_extra_source(self, deb_source):

        install_extra_source([['mongodb', 'http://downloads-distro.mongodb.org/repo/ubuntu-upstart', 'dist', '10gen'],])
        self.assertTrue(deb_source.called)
        self.assertEqual(deb_source.call_args, call('mongodb', 'http://downloads-distro.mongodb.org/repo/ubuntu-upstart', 'dist', '10gen'))

    @patch('fabtools.require.deb.package', return_value=Mock())
    @patch('fabtools.require.deb.source', return_value=Mock())
    @patch('fabtools.require.deb.ppa', return_value=Mock())
    @patch('fabtools.require.deb.packages', return_value=Mock())
    @patch('fabtools.system.distrib_release', return_value='13')
    @patch('fabtools.system.distrib_id', return_value='Ubuntu')
    @patch('pydiploy.require.system.package_installed', return_value=False)
    def test_check_python3_install(self, pkg_installed, sys_distrib, sys_distrib_id, deb_pkgs, deb_ppa, deb_source, deb_pkg):

        check_python3_install()
        self.assertTrue(deb_pkgs.called)
        self.assertTrue(deb_ppa.called)
        self.assertTrue(deb_pkg.called)
