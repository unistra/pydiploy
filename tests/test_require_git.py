#!/usr/bin/env python
# -*- coding: utf-8 -*-

import copy
from unittest import TestCase

from fabric.api import env
from mock import call, Mock, patch
from pydiploy.require.git import (archive, check_tag_exist, collect_branches,
                                  collect_tags)


class GitCheck(TestCase):

    """
    test for git
    """

    def setUp(self):
        self.previous_env = copy.deepcopy(env)
        self.filename = "myfile"
        self.remote = "remote"
        self.prefix = "prefix"

    def tearDown(self):
        env.clear()
        env.update(self.previous_env)

    @patch('fabric.api.abort', return_value=Mock())
    @patch('fabric.api.lcd', return_value=Mock())
    @patch('fabric.api.local', return_value=Mock())
    def test_archive(self, api_local, api_lcd, api_abort):

        api_lcd.return_value.__exit__ = Mock()
        api_lcd.return_value.__enter__ = Mock()

        archive(self.filename)

        self.assertFalse(api_abort.called)
        self.assertTrue(api_lcd.called)
        self.assertEqual(api_lcd.call_args, call('.'))

        self.assertTrue(api_local.called)
        self.assertEqual(api_local.call_args, call(
            'git archive --format=tar HEAD |gzip > /tmp/myfile.tar.gz'))

        # if remote and prefix
        archive(self.filename, remote=self.remote, prefix=self.prefix)
        self.assertTrue(api_local.called)
        self.assertEqual(api_local.call_args, call(
            'git archive --format=tar --remote=remote --prefix=prefix HEAD |gzip > /tmp/myfile.tar.gz'))

        # if remote and prefix and specific folder
        archive(self.filename, remote=self.remote, prefix=self.prefix, specific_folder='/myfolder')
        self.assertTrue(api_local.called)
        self.assertEqual(api_local.call_args, call(
            'git archive --format=tar --remote=remote --prefix=prefix HEAD:/myfolder |gzip > /tmp/myfile.tar.gz'))

        # if format not supported
        archive(self.filename, format="error")
        self.assertTrue(api_abort.called)
        self.assertEqual(api_abort.call_args, call(
            'Git archive format not supported: error'))

    @patch('fabric.api.lcd', return_value=Mock())
    @patch('fabric.context_managers.hide', return_value=Mock())
    def test_collect_tags(self, fabric_hide, api_lcd):

        fabric_hide.return_value.__exit__ = Mock()
        fabric_hide.return_value.__enter__ = Mock()

        api_lcd.return_value.__exit__ = Mock()
        api_lcd.return_value.__enter__ = Mock()
        collect_tags(project_path='.', remote=None)
        self.assertTrue(api_lcd.called)
        self.assertEqual(api_lcd.call_args, call('.'))
        collect_tags(project_path='.', remote=True)

    @patch('fabric.api.lcd', return_value=Mock())
    @patch('fabric.context_managers.hide', return_value=Mock())
    def test_collect_branches(self, fabric_hide, api_lcd):
        fabric_hide.return_value.__exit__ = Mock()
        fabric_hide.return_value.__enter__ = Mock()

        api_lcd.return_value.__exit__ = Mock()
        api_lcd.return_value.__enter__ = Mock()
        collect_branches(project_path='.', remote=None)
        self.assertTrue(api_lcd.called)
        self.assertEqual(api_lcd.call_args, call('.'))
        collect_branches(project_path='.', remote=True)

    @patch('pydiploy.require.git.collect_tags', return_value=['test',])
    @patch('pydiploy.require.git.collect_branches', return_value=['test',])
    def test_check_tag_exist(self, collect_branches, collect_tags):

        check_tag_exist(tag="master")

        check_tag_exist(tag="test")
