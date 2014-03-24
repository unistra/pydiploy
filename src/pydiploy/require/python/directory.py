# -*- coding: utf-8 -*-

"""
"""

import os

from fabric.api import env
from fabric.api import cd
from fabric.api import run
from fabric.contrib.files import exists

import fabtools
from fabtools import require

from pydiploy.system import remote_home


def install(tmp_directory):
    """
    """
    require('virtualenvdir')
    with fabtools.python.virtualenv(env.virtualenvdir):
        with cd(tmp_directory):
            run('python setup.py install')
            if exists('requirements/%s.txt' % env.env):
                require.python.requirements('requirements/%s.txt' % env.env)


def appdir(user, group, app_name):
    """
    """
    if not env.has_key('appdir'):
        env.appdir = os.path.join(remote_home(user), app_name)
        require.directory(env.appdir, use_sudo=True, owner=user, group=group,
                          mode='755')
    return env.appdir


def logdir(user, group, app_name):
    """
    """
    if not env.has_key('logdir'):
        env.logdir = os.path.join(appdir(user, group, app_name), 'log')
        require.directory(env.logdir, use_sudo=True, owner=user, group=group,
                          mode='755')
    return env.logdir


def application_directories():
    with cd(env.remote_project_dir):
        fabtools.require.directory('log',
                                   use_sudo=True,
                                   owner=env.remote_owner,
                                   group=env.remote_group,
                                   mode='755')
