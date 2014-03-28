#!/usr/bin/env python
# -*- coding: utf-8 -*-

from unittest import TestCase
from fabric.api import env
from mock import patch, call, Mock
from pydiploy.require.git import archive

class GitCheck(TestCase):
    """
    test for git
    """

    def setUp(self):
        self.filename = "myfile"
        self.remote = "remote"
        self.prefix = "prefix"


    def tearDown(self):
        env.clear()


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
        self.assertEqual(api_local.call_args, call('git archive --format=tar HEAD |gzip > /tmp/myfile.tar.gz'))


        # if remote and prefix
        archive(self.filename, remote=self.remote, prefix=self.prefix)
        self.assertTrue(api_local.called)
        self.assertEqual(api_local.call_args, call('git archive --format=tar --remote=remote --prefix=prefix HEAD |gzip > /tmp/myfile.tar.gz'))


        # if format not supported
        archive(self.filename, format="error")
        self.assertTrue(api_abort.called)
        self.assertEqual(api_abort.call_args, call('Git archive format not supported: error'))
        
       