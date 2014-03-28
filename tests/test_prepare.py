#!/usr/bin/env python
# -*- coding: utf-8 -*-

from unittest import TestCase
from fabric.api import env
from mock import patch, call, Mock
from pydiploy.prepare import oracle_client, sap_client, tag, build_env


class PrepareCheck(TestCase):
    """
    test for circus
    """

    def setUp(self):
        pass


    def test_oracle_client(self):
        pass


    def test_sap_client(self):
        pass


    def test_tag(self):
        tag("4.0")
        self.assertEqual(env.tag, "4.0")


    def test_build_env(self):
        pass
        