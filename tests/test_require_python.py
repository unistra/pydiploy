#!/usr/bin/env python
# -*- coding: utf-8 -*-

from unittest import TestCase
from pydiploy.require.python.utils import python_pkg, application_dependencies
from fabric.api import env
from mock import patch, call, Mock


class UtilsCheck(TestCase):

    """
    Test the require python directory package
    """

    def setUp(self):
        # env
        env.remote_virtualenv_dir = "remote_virtualenv_dir"
        env.remote_current_path = "remote_current_path"
        env.goal = "goal"
        env.remote_owner = "remote_owner"
        env.host_string = 'hosttest'


    @patch('fabtools.require.deb.packages', return_value=True)
    @patch('fabtools.require.python.install', return_value=True)
    def test_python_pkg(self, python_install, deb_packages):
        python_pkg()
        self.assertTrue(deb_packages.called)
        self.assertEqual(deb_packages.call_args, call(['python-dev', 'python-pip'], update=False))
        self.assertTrue(python_install.called)
        self.assertEqual(python_install.call_args, call('pip', upgrade=True, use_sudo=True))
        
        


    @patch('fabtools.python.virtualenv', return_value=Mock())
    @patch('fabric.api.cd', return_value=Mock())
    @patch('fabric.api.sudo', return_value=Mock())
    @patch('fabtools.python.install_requirements', return_value=True)
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
        self.assertEqual(install_requirements.call_args, call('requirements/goal.txt', use_sudo=True, upgrade=False, user='remote_owner'))


