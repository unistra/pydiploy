#!/usr/bin/env python
# -*- coding: utf-8 -*-

from unittest import TestCase
from fabric.api import env
from mock import patch, call, Mock
from pydiploy.require.django.command import django_prepare


class CommandCheck(TestCase):

    """
    test command django
    """

    def setUp(self):
        env.remote_virtualenv_dir = "remote_virtualenv_dir"
        env.remote_current_path = "remote_current_path"
        env.local_tmp_dir = "local_tmp_dir"
        env.remote_owner = "remote_owner"
        env.remote_base_package_dir = "remote_base_package_dir"


    @patch('fabtools.python.virtualenv', return_value=Mock())
    @patch('fabric.api.cd', return_value=Mock())
    @patch('fabric.api.settings', return_value=Mock())
    @patch('fabric.api.sudo', return_value=Mock())
    @patch('fabtools.files.is_dir', return_value=Mock())
    @patch('fabric.api.get', return_value=Mock())
    def test_django_prepare(self, api_get, files_is_dir, api_sudo, api_settings, api_cd, python_virtualenv):

        python_virtualenv.return_value.__exit__ = Mock()
        python_virtualenv.return_value.__enter__ = Mock()

        api_cd.return_value.__exit__ = Mock()
        api_cd.return_value.__enter__ = Mock()

        api_settings.return_value.__exit__ = Mock()
        api_settings.return_value.__enter__ = Mock()

        django_prepare()

        self.assertTrue(python_virtualenv.called)
        self.assertEqual(python_virtualenv.call_args, call('remote_virtualenv_dir'))

        self.assertTrue(api_cd.called)
        self.assertEqual(api_cd.call_args, call('remote_current_path'))

        self.assertTrue(api_settings.called)
        self.assertEqual(api_settings.call_args, call(sudo_user='remote_owner'))

        self.assertTrue(api_settings.called)
        self.assertEqual(api_settings.call_args, call(sudo_user='remote_owner'))

        self.assertTrue(files_is_dir.called)
        self.assertEqual(files_is_dir.call_args, call('remote_base_package_dir/locale'))

        self.assertTrue(api_get.called)
        self.assertEqual(api_get.call_args, call('remote_current_path/assets', local_path='local_tmp_dir'))

        self.assertTrue(api_sudo.called)
        self.assertEqual(api_sudo.call_args_list, [call('python manage.py syncdb --noinput'),
                                call('python manage.py migrate'),
                                call('python manage.py compilemessages'),
                                call('python manage.py collectstatic --noinput -i admin -i rest_framework -i django_extensions')])
         

        