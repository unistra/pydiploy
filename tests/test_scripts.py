#!/usr/bin/env python
# -*- coding: utf-8 -*-

import copy
from unittest import TestCase

from fabric.api import env
from mock import call, Mock, patch
from pydiploy.scripts import get_dest_files, sublime_text_snippet


class ScriptsCheck(TestCase):

    """
    scripts test
    """

    def setUp(self):
        self.previous_env = copy.deepcopy(env)


    def tearDown(self):
        env.clear()
        env.update(self.previous_env)


    def test_get_dest_files(self):
        get_dest_files('Linux')

        # test NotImplemented system
        self.assertRaises(NotImplementedError, get_dest_files, 'amigaos')


    def test_sublime_text_snippet(self):
        sublime_text_snippet()
