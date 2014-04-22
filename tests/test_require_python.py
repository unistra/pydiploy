#!/usr/bin/env python
# -*- coding: utf-8 -*-

from unittest import TestCase
from pydiploy.require.python.utils import python_pkg, application_dependencies
from pydiploy.require.python.virtualenv import virtualenv
from fabric.api import env
from mock import patch, call, Mock


class UtilsCheck(TestCase):

    """
    Test the require python directory package
    """

    def setUp(self):
        env.remote_virtualenv_dir = "remote_virtualenv_dir"
        env.remote_current_path = "remote_current_path"
        env.goal = "goal"
        env.remote_owner = "remote_owner"
        env.host_string = 'hosttest'
        env.remote_python_version = 2.7


    def tearDown(self):
        env.clear()


    @patch('fabtools.require.deb.packages', return_value=Mock())
    @patch('fabtools.require.python.install', return_value=Mock())
    def test_python_pkg(self, python_install, deb_packages):
        python_pkg()
        self.assertTrue(deb_packages.called)
        self.assertEqual(deb_packages.call_args, call(['python-dev', 'python-pip'], update=False))
        self.assertTrue(python_install.called)
        self.assertEqual(python_install.call_args, call('pip', upgrade=True, use_sudo=True))
        
        
    @patch('fabtools.python.virtualenv', return_value=Mock())
    @patch('fabric.api.cd', return_value=Mock())
    @patch('fabric.api.sudo', return_value=Mock())
    @patch('fabtools.python.install_requirements', return_value=Mock())
    def test_application_dependencies(self, install_requirements, api_sudo, api_cd, python_virtualenv):

        python_virtualenv.return_value.__exit__ = Mock()
        python_virtualenv.return_value.__enter__ = Mock()

        api_cd.return_value.__exit__ = Mock()
        api_cd.return_value.__enter__ = Mock()

        application_dependencies(False)

        self.assertTrue(api_cd.called)
        self.assertEqual(api_cd.call_args, call('remote_current_path'))

        self.assertTrue(api_sudo.called)
        self.assertEqual(api_sudo.call_args, call('pip install -e .', user='remote_owner', pty=False))
   
        self.assertTrue(python_virtualenv.called)
        self.assertEqual(python_virtualenv.call_args, call('remote_virtualenv_dir'))

        self.assertTrue(install_requirements.called)
        self.assertEqual(install_requirements.call_args, call('requirements/goal.txt', pip_cmd='pip', use_sudo=True, upgrade=False, user='remote_owner'))


class VirtualEnvCheck(TestCase):

    """
    class to test virtualenv
    """

    def setUp(self):
        env.remote_group = "remote_group"
        env.remote_python_version = "2.7"
        env.remote_virtualenv_dir = "remote_virtualenv_dir"
        env.remote_owner = "remote_owner"


    def tearDown(self):
        env.clear()


    @patch('fabtools.require.files.directory', return_value=Mock())
    @patch('fabtools.require.python.virtualenv', return_value=Mock())
    def test_virtualenv(self, python_virtualenv, files_directory):

        virtualenv()

        self.assertTrue(python_virtualenv.called)
        self.assertEqual(python_virtualenv.call_args, 
            call('remote_virtualenv_dir', clear=False, use_sudo=True, venv_python='/usr/bin/python2.7', user='remote_owner'))

        self.assertTrue(files_directory.called)
        self.assertEqual(files_directory.call_args, call('remote_virtualenv_dir', owner='remote_owner', use_sudo=True, group='remote_group'))

        