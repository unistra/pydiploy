#!/usr/bin/env python
# -*- coding: utf-8 -*-

from unittest import TestCase
from fabric.api import env
from mock import patch, call, Mock
from pydiploy.require.django.command import django_prepare
from pydiploy.require.django.utils import generate_secret_key, extract_settings, app_settings


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

    def tearDown(self):
        env.clear()


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
         

class UtilsCheck(TestCase):

    """
    utils test
    """
    def setUp(self):
        env.remote_settings_file = "remote_settings_file"
        env.local_tmp_dir = "tests/data"
        env.goal = "settings"
        env.map_settings = {"secret_key": "SECRET_KEY", "default_db_user": "DATABASES['default']['USER']"}
        env.local_tmp_root_app_package = "local_tmp_root_app_package"
        env.remote_owner = "owner"


    def tearDown(self):
        env.clear()


    def test_generate_secret_key(self):
        generate_secret_key()
        self.assertIsNotNone(env.secret_key)


    @patch('fabric.api.get', return_value=Mock())
    def test_extract_settings(self, api_get):
        extract_settings()

        self.assertTrue(api_get.called)
        self.assertEqual(api_get.call_args, call('remote_settings_file', local_path='tests/data'))

        self.assertEqual(env.secret_key, '{{ secret_key }}')
        self.assertEqual(env.default_db_user, '{{ default_db_user }}')


    @patch('fabtools.files.is_file', return_value=True)
    @patch('fabric.api.execute', return_value=Mock())
    @patch('fabric.api.require', return_value=Mock())
    @patch('fabtools.files.upload_template', return_value=Mock())
    def test_app_settings(self, upload_template, api_require, api_execute, is_file):
        
        # is file true
        app_settings(test1='toto')
        
        self.assertTrue(is_file.called)
        self.assertEqual(is_file.call_args, call(path='remote_settings_file', use_sudo=True))

        self.assertTrue(api_execute.called)
        self.assertTrue(str(api_execute.call_args).find('extract_settings') > 0)

        self.assertEqual(env.test1, 'toto')

        self.assertTrue(api_require.called)
        self.assertTrue(str(api_require.call_args).find('secret_key') > 0)
        self.assertTrue(str(api_require.call_args).find('default_db_user') > 0)

        self.assertTrue(upload_template.called)
        self.assertTrue(str(upload_template.call_args).find("template_dir='local_tmp_root_app_package/settings'") > 0)
        self.assertTrue(str(upload_template.call_args).find("'settings.py'") > 0)
        self.assertTrue(str(upload_template.call_args).find("'remote_settings_file'") > 0)
        self.assertTrue(str(upload_template.call_args).find("use_jinja=True") > 0)
        self.assertTrue(str(upload_template.call_args).find("user='owner'") > 0)
      
        # is file false
        is_file.return_value = False

        app_settings()

        self.assertTrue(is_file.called)
        self.assertEqual(is_file.call_args, call(path='remote_settings_file', use_sudo=True))

        self.assertTrue(api_execute.called)
        self.assertTrue(str(api_execute.call_args).find('generate_secret_key') > 0)





        

