#!/usr/bin/env python
# -*- coding: utf-8 -*-

import copy
import datetime
import re
from unittest import TestCase

from fabric.api import env
from mock import call, Mock, patch
from pydiploy.require.django.command import (django_custom_cmd,
                                             django_dump_database,
                                             django_get_version,
                                             django_prepare)
from pydiploy.require.django.utils import (app_settings, deploy_manage_file,
                                           deploy_wsgi_file, extract_settings,
                                           generate_secret_key)


class CommandCheck(TestCase):

    """
    test command django
    """

    def setUp(self):
        self.previous_env = copy.deepcopy(env)
        env.remote_virtualenv_dir = "remote_virtualenv_dir"
        env.remote_current_path = "remote_current_path"
        env.local_tmp_dir = "local_tmp_dir"
        env.remote_owner = "remote_owner"
        env.remote_base_package_dir = "remote_base_package_dir"
        env.dest_path = ""
        self.dump_name = '%s.json' % datetime.datetime.today().strftime(
            "%Y_%m_%d-%H%M")

    def tearDown(self):
        env.clear()
        env.update(self.previous_env)

    @patch('fabric.api.lcd', return_value=Mock())
    @patch('fabric.api.local', return_value=Mock())
    @patch('fabtools.python.virtualenv', return_value=Mock())
    @patch('fabric.api.cd', return_value=Mock())
    @patch('fabric.api.settings', return_value=Mock())
    @patch('fabric.api.sudo', return_value=Mock())
    @patch('fabric.api.get', return_value=Mock())
    @patch('pydiploy.require.django.command.django_get_version', return_value="1.8")
    def test_django_prepare(self, django_get_version, api_get, api_sudo, api_settings, api_cd, python_virtualenv, api_local, api_lcd):

        api_lcd.return_value.__exit__ = Mock()
        api_lcd.return_value.__enter__ = Mock()

        python_virtualenv.return_value.__exit__ = Mock()
        python_virtualenv.return_value.__enter__ = Mock()

        api_cd.return_value.__exit__ = Mock()
        api_cd.return_value.__enter__ = Mock()

        api_settings.return_value.__exit__ = Mock()
        api_settings.return_value.__enter__ = Mock()

        django_prepare()

        self.assertTrue(python_virtualenv.called)
        self.assertEqual(
            python_virtualenv.call_args, call('remote_virtualenv_dir'))

        self.assertTrue(api_cd.called)
        self.assertEqual(api_cd.call_args, call('remote_current_path'))

        self.assertTrue(api_settings.called)
        self.assertEqual(api_settings.call_args, call(warn_only=True))

        self.assertTrue(api_settings.called)
        self.assertEqual(api_settings.call_args, call(warn_only=True))

        self.assertTrue(api_get.called)
        self.assertEqual(api_get.call_args, call(
            'remote_current_path/assets', local_path='local_tmp_dir'))

        self.assertTrue(api_sudo.called)
        self.assertEqual(
            api_sudo.call_args_list, [
                # call('python -c "import django;print(django.get_version())"'),
                # call('python manage.py syncdb --noinput'),
                call('python manage.py migrate'),
                call('python manage.py compilemessages'),
                call('python manage.py collectstatic --noinput')]) 



    @patch('fabric.api.lcd', return_value=Mock())
    @patch('fabric.api.local', return_value=Mock())
    @patch('fabtools.python.virtualenv', return_value=Mock())
    @patch('fabric.api.cd', return_value=Mock())
    @patch('fabric.api.settings', return_value=Mock())
    @patch('fabric.api.sudo', return_value=Mock())
    @patch('fabric.api.get', return_value=Mock())
    @patch('pydiploy.require.django.command.django_get_version', return_value="1.6")
    def test_django_prepare(self, django_get_version, api_get, api_sudo, api_settings, api_cd, python_virtualenv, api_local, api_lcd):

        api_lcd.return_value.__exit__ = Mock()
        api_lcd.return_value.__enter__ = Mock()

        python_virtualenv.return_value.__exit__ = Mock()
        python_virtualenv.return_value.__enter__ = Mock()

        api_cd.return_value.__exit__ = Mock()
        api_cd.return_value.__enter__ = Mock()

        api_settings.return_value.__exit__ = Mock()
        api_settings.return_value.__enter__ = Mock()

        django_prepare()

        self.assertTrue(python_virtualenv.called)
        self.assertEqual(
            python_virtualenv.call_args, call('remote_virtualenv_dir'))

        self.assertTrue(api_cd.called)
        self.assertEqual(api_cd.call_args, call('remote_current_path'))

        self.assertTrue(api_settings.called)
        self.assertEqual(api_settings.call_args, call(warn_only=True))

        self.assertTrue(api_settings.called)
        self.assertEqual(api_settings.call_args, call(warn_only=True))

        self.assertTrue(api_get.called)
        self.assertEqual(api_get.call_args, call(
            'remote_current_path/assets', local_path='local_tmp_dir'))

        self.assertTrue(api_sudo.called)
        self.assertEqual(
            api_sudo.call_args_list, [
                # call('python -c "import django;print(django.get_version())"'),
                call('python manage.py syncdb --noinput'),
                call('python manage.py migrate'),
                call('python manage.py compilemessages'),
                call('python manage.py collectstatic --noinput')]) 




    @patch('fabtools.python.virtualenv', return_value=Mock())
    @patch('fabric.api.cd', return_value=Mock())
    @patch('fabric.api.settings', return_value=Mock())
    @patch('fabric.api.sudo', return_value=Mock())
    @patch('fabric.api.get', return_value=Mock())
    def test_django_dump_database(self, api_get, api_sudo, api_settings, api_cd, python_virtualenv):

        python_virtualenv.return_value.__exit__ = Mock()
        python_virtualenv.return_value.__enter__ = Mock()

        api_cd.return_value.__exit__ = Mock()
        api_cd.return_value.__enter__ = Mock()

        api_settings.return_value.__exit__ = Mock()
        api_settings.return_value.__enter__ = Mock()

        django_dump_database()

        self.assertTrue(python_virtualenv.called)
        self.assertEqual(
            python_virtualenv.call_args, call('remote_virtualenv_dir'))

        self.assertTrue(api_cd.called)
        self.assertEqual(api_cd.call_args, call('remote_current_path'))

        self.assertTrue(api_settings.called)
        self.assertEqual(
            api_settings.call_args, call(sudo_user=env.remote_owner))

        self.assertTrue(api_sudo.called)
        self.assertEqual(api_sudo.call_args, call(
            'python manage.py dumpdata --indent=4 > /tmp/%s ' % self.dump_name))

        self.assertTrue(api_get.called)
        self.assertEqual(api_get.call_args, call(
            '/tmp/%s' % self.dump_name, local_path=env.dest_path))

    @patch('fabtools.python.virtualenv', return_value=Mock())
    @patch('fabric.api.cd', return_value=Mock())
    @patch('fabric.api.settings', return_value=Mock())
    @patch('fabric.api.sudo', return_value=Mock())
    def test_django_custom_cmd(self, api_sudo, api_settings, api_cd, python_virtualenv):

        python_virtualenv.return_value.__exit__ = Mock()
        python_virtualenv.return_value.__enter__ = Mock()

        api_cd.return_value.__exit__ = Mock()
        api_cd.return_value.__enter__ = Mock()

        api_settings.return_value.__exit__ = Mock()
        api_settings.return_value.__enter__ = Mock()
        django_custom_cmd('test')


    @patch('fabtools.python.virtualenv', return_value=Mock())
    @patch('fabric.api.cd', return_value=Mock())
    @patch('fabric.api.settings', return_value=Mock())
    @patch('fabric.api.sudo', return_value=Mock())
    def test_django_get_version(self, api_sudo, api_settings, api_cd, python_virtualenv):

        python_virtualenv.return_value.__exit__ = Mock()
        python_virtualenv.return_value.__enter__ = Mock()

        api_cd.return_value.__exit__ = Mock()
        api_cd.return_value.__enter__ = Mock()

        api_settings.return_value.__exit__ = Mock()
        api_settings.return_value.__enter__ = Mock()

        django_get_version()

        self.assertTrue(python_virtualenv.called)
        self.assertEqual(
            python_virtualenv.call_args, call('remote_virtualenv_dir'))

        self.assertTrue(api_cd.called)
        self.assertEqual(api_cd.call_args, call('remote_current_path'))

        self.assertTrue(api_settings.called)
        self.assertEqual(api_settings.call_args, call(sudo_user='remote_owner'))

        self.assertTrue(api_sudo.called)
        self.assertEqual(
            api_sudo.call_args_list, [
                call('python -c "import django;print(django.get_version())"')])



class UtilsCheck(TestCase):

    """
    utils test
    """

    def setUp(self):
        self.previous_env = copy.deepcopy(env)
        env.remote_settings_file = "remote_settings_file"
        env.local_tmp_dir = "tests/data"
        env.goal = "settings"
        env.map_settings = {
            "secret_key": "SECRET_KEY",
            "default_db_user": "DATABASES['default']['USER']",
            'thanks_arno': ('THANKS_ARNAUD',
                            r'environ.get\(["\']THANKS_ARNAUD[\'"], [\'"](.*)["\']\)')}
        env.local_tmp_root_app_package = "local_tmp_root_app_package"
        env.remote_owner = "owner"
        env.previous_settings_file = "remote_settings_file"
        env.remote_current_release = "remote_current_release"
        env.remote_base_package_dir = "remove_base_package_dir"
        env.local_tmp_root_app = "local_tmp_root_path"

    def tearDown(self):
        env.clear()
        env.update(self.previous_env)

    def test_generate_secret_key(self):
        generate_secret_key()
        self.assertIsNotNone(env.secret_key)

    @patch('fabric.api.get', return_value=Mock())
    def test_extract_settings(self, api_get):

        extract_settings()

        self.assertTrue(api_get.called)
        self.assertEqual(api_get.call_args, call(
            'remote_settings_file', local_path='tests/data'))

        self.assertEqual(env.secret_key, '{{ secret_key }}')
        self.assertEqual(env.default_db_user, '{{ default_db_user }}')

    @patch('fabtools.files.is_file', return_value=Mock())
    @patch('fabric.api.execute', return_value=Mock())
    @patch('fabric.api.require', return_value=Mock())
    @patch('fabtools.files.upload_template', return_value=Mock())
    def test_app_settings(self, upload_template, api_require, api_execute, is_file):

        # is file true
        app_settings(test1='toto')

        self.assertTrue(is_file.called)
        self.assertEqual(is_file.call_args, call(
            path='remote_settings_file', use_sudo=True))

        self.assertTrue(api_execute.called)
        self.assertTrue(
            str(api_execute.call_args).find('extract_settings') > 0)

        self.assertEqual(env.test1, 'toto')

        self.assertTrue(api_require.called)
        self.assertTrue(str(api_require.call_args).find('secret_key') > 0)
        self.assertTrue(str(api_require.call_args).find('default_db_user') > 0)

        self.assertTrue(upload_template.called)
        self.assertTrue(str(upload_template.call_args).find(
            "template_dir='local_tmp_root_app_package/settings'") > 0)
        self.assertTrue(
            str(upload_template.call_args).find("'settings.py'") > 0)
        self.assertTrue(
            str(upload_template.call_args).find("'remote_settings_file'") > 0)
        self.assertTrue(
            str(upload_template.call_args).find("use_jinja=True") > 0)
        self.assertTrue(
            str(upload_template.call_args).find("user='owner'") > 0)

        # is file false
        is_file.return_value = False

        app_settings()

        self.assertTrue(is_file.called)
        self.assertEqual(is_file.call_args, call(
            path='remote_settings_file', use_sudo=True))

        self.assertTrue(api_execute.called)
        self.assertTrue(
            str(api_execute.call_args).find('generate_secret_key') > 0)

    @patch('fabtools.files.upload_template', return_value=Mock())
    def test_deploy_manage_file(self, upload_template):

        deploy_manage_file()
        self.assertTrue(upload_template.called)
        # self.assertTrue(str(upload_template.call_args).find(
        #     "template_dir='local_tmp_root_app_package/settings'") > 0)
        # self.assertTrue(
        #     str(upload_template.call_args).find("'settings.py'") > 0)
        # self.assertTrue(
        #     str(upload_template.call_args).find("'remote_settings_file'") > 0)
        # self.assertTrue(
        #     str(upload_template.call_args).find("use_jinja=True") > 0)
        # self.assertTrue(
        #     str(upload_template.call_args).find("user='owner'") > 0)

    @patch('fabtools.files.upload_template', return_value=Mock())
    def test_deploy_wsgi_file(self, upload_template):

        deploy_wsgi_file()
        self.assertTrue(upload_template.called)
        # self.assertTrue(str(upload_template.call_args).find(
        #     "template_dir='local_tmp_root_app_package/settings'") > 0)
        # self.assertTrue(
        #     str(upload_template.call_args).find("'settings.py'") > 0)
        # self.assertTrue(
        #     str(upload_template.call_args).find("'remote_settings_file'") > 0)
        # self.assertTrue(
        #     str(upload_template.call_args).find("use_jinja=True") > 0)
        # self.assertTrue(
        #     str(upload_template.call_args).find("user='owner'") > 0)
