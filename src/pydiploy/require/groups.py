"""
"""

from fabric.api import hide
from fabric.api import settings
from fabric.api import sudo
from fabric.api import run


def exists(name):
    with settings(hide('running', 'stdout', 'warnings'), warn_only=True):
        return run('getent group %s' % name).succeeded


def create(name):
    if not exists(name):
        sudo('addgroup %s' % name)
