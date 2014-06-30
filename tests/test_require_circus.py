#!/usr/bin/env python
# -*- coding: utf-8 -*-

from unittest import TestCase
from fabric.api import env
from mock import patch, call, Mock
from pydiploy.require.circus import circus_pkg, app_circus_conf, upstart, app_reload


class CircusCheck(TestCase):
    """
    test for circus
    """

    def setUp(self):
        env.remote_home = 'remote_home'
        env.lib_path = 'lib_path'
        env.remote_owner = 'remote_owner'
        env.remote_group = 'remote_group'
        env.application_name = "application_name"


    def tearDown(self):
        env.clear()


    @patch('fabtools.system.distrib_id', return_value='Ubuntu')
    @patch('fabtools.system.distrib_release', return_value='10.04')
    @patch('fabtools.require.deb.packages', return_value=Mock())
    @patch('fabtools.require.deb.ppa', return_value=Mock())
    @patch('fabtools.require.python.install', return_value=Mock())
    @patch('fabtools.files.upload_template', return_value=Mock())
    @patch('fabtools.require.files.directory', return_value=Mock())
    def test_circus_pkg(self, files_directory, upload_template, python_install, deb_ppa, deb_packages, distrib_release, distrib_id):
        circus_pkg()

        self.assertTrue(distrib_release.called)
        self.assertTrue(distrib_id.called)

        self.assertTrue(deb_packages.called)
        self.assertEqual(deb_packages.call_args_list, [call(['python-software-properties'], update=False),
            call(['libzmq-dev', 'libevent-dev'], update=False)])
        
        self.assertTrue(deb_ppa.called)
        self.assertEqual(deb_ppa.call_args_list, [call('ppa:chris-lea/zeromq'), call('ppa:chris-lea/libpgm')])

        self.assertTrue(python_install.called)
        self.assertEqual(python_install.call_args_list, [call('gevent', use_sudo=True),
            call('circus', use_sudo=True), call('circus-web', use_sudo=True)])

        self.assertTrue(upload_template.called)  
        self.assertTrue(str(upload_template.call_args).find("'circus.ini.tpl'") > 0)
        self.assertTrue(str(upload_template.call_args).find("'remote_home/.circus.ini'") > 0)
        self.assertTrue(str(upload_template.call_args).find("template_dir='lib_path/templates'") > 0)
        self.assertTrue(str(upload_template.call_args).find("user='remote_owner'") > 0)
      
        self.assertTrue(files_directory.called)
        self.assertEqual(files_directory.call_args, 
            call(owner='remote_owner', path='remote_home/.circus.d', use_sudo=True, group='remote_group', mode='750'))


    @patch('fabtools.files.upload_template', return_value=Mock())
    def test_app_circus_conf(self, upload_template):
        app_circus_conf()
        
        self.assertTrue(upload_template.called)  
        self.assertTrue(str(upload_template.call_args).find("'app.ini.tpl'") > 0)
        self.assertTrue(str(upload_template.call_args).find("'remote_home/.circus.d/application_name.ini'") > 0)
        self.assertTrue(str(upload_template.call_args).find("template_dir='lib_path/templates'") > 0)
        self.assertTrue(str(upload_template.call_args).find("user='remote_owner'") > 0)

    @patch('fabtools.files.upload_template', return_value=Mock())
    def test_upstart(self, upload_template):
        upstart()
        
        self.assertTrue(upload_template.called)  
        self.assertTrue(str(upload_template.call_args).find("'upstart.conf.tpl'") > 0)
        self.assertTrue(str(upload_template.call_args).find("'/etc/init/circus.conf'") > 0)
        self.assertTrue(str(upload_template.call_args).find("template_dir='lib_path/templates'") > 0)
        self.assertTrue(str(upload_template.call_args).find("user='root'") > 0)

    @patch('fabric.api.settings', return_value=Mock())
    @patch('fabric.api.sudo', return_value='running')
    def test_app_reload(self, api_sudo, api_settings):

        api_settings.return_value.__exit__ = Mock()
        api_settings.return_value.__enter__ = Mock()

        # test if running
        app_reload()

        self.assertTrue(api_sudo.called)
        self.assertEqual(api_sudo.call_args_list, [call('status circus'), call('circusctl reloadconfig'), call('circusctl restart application_name')])

        self.assertTrue(api_settings.called)  
        self.assertEqual(api_settings.call_args, call(sudo_user='remote_owner')) 

        # test if not running
        api_sudo.return_value='stopped'
        api_sudo.called = False
        api_settings.called = False

        app_reload()

        self.assertTrue(api_sudo.called)
        self.assertEqual(api_sudo.call_args, call('start circus'))
        self.assertFalse(api_settings.called)


