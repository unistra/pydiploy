#!/usr/bin/env python
# -*- coding: utf-8 -*-

from unittest import TestCase
from fabric.api import env
from mock import patch, call, Mock
from pydiploy.require.system import django_user, django_group, update_pkg_index, set_locale, set_timezone, permissions


class SystemCheck(TestCase):
    """
    test for System
    """
    def setUp(self):
        env.remote_group = "remote_group"
        env.remote_owner = "remote_owner"
        env.locale = "FR_fr"
        env.server_name = "server_name"
        env.timezone = "mytimezone"
        env.remote_project_dir = "remote_project_dir"


    def tearDown(self):
        env.clear()


    @patch('fabtools.require.group', return_value=Mock())
    @patch('fabtools.require.user', return_value=Mock())
    @patch('fabtools.require.sudoer', return_value=Mock())
    def test_django_user(self, require_group, require_user, require_sudoer):
        django_user(commands='mycommand')

        self.assertTrue(require_group.called)
        self.assertEqual(require_group.call_args, call('%remote_group', passwd=False, commands='mycommand', operators='remote_owner,root'))

        self.assertTrue(require_user.called)
        self.assertEqual(require_user.call_args, call('remote_owner', create_group=True, shell='/bin/bash', group='remote_group', create_home=True))

        self.assertTrue(require_sudoer.called)
        self.assertEqual(require_sudoer.call_args, call('remote_group'))


    @patch('fabtools.require.group', return_value=Mock())
    def test_django_group(self, require_group):
        django_group("mygroup")
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

        api_run.return_value= "otherlocale"

        set_locale()

        self.assertTrue(api_run.called)
        self.assertTrue(api_sudo.called)
        self.assertEqual(api_sudo.call_args_list, [call('locale-gen FR_fr'), call('/usr/sbin/update-locale LANG=FR_fr')])


    @patch('fabtools.system.distrib_id', return_value='Notsupported')
    @patch('fabric.api.sudo', return_value=Mock())
    def test_set_timezone(self, api_sudo, distrib_id):
        set_timezone()
        # test error
        self.assertTrue(distrib_id.called)
        self.assertFalse(api_sudo.called)

        # test if it works
        distrib_id.return_value = 'Ubuntu'
        set_timezone()
        self.assertTrue(distrib_id.called)
        self.assertTrue(api_sudo.called)

        self.assertEqual(api_sudo.call_args, call('cp -f /usr/share/zoneinfo/mytimezone /etc/localtime'))


    @patch('fabric.api.sudo', return_value=Mock())
    def test_permissions(self, api_sudo):
        permissions()
        self.assertTrue(api_sudo.called)
        self.assertEqual(api_sudo.call_args, call('chmod -R g+w remote_project_dir'))

        

        


        