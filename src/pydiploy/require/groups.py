# -*- coding: utf-8 -*-

"""
"""

from fabric.api import hide, settings, sudo, run


def exists(name):
    with settings(hide('running', 'stdout', 'warnings'), warn_only=True):
        return run('getent group %s' % name).succeeded


def create(name):
    if not exists(name):
        sudo('addgroup %s' % name)
