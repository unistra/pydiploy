"""
"""

import os

from fabric.api import cd
from fabric.api import env
from fabric.api import get
from fabric.api import put
from fabric.api import require
from fabric.api import run
from fabric.api import sudo
from fabric.api import shell_env

import fabtools

from ...system import remote_home


def staticfiles(user=None):
    require('virtualenvdir', 'appdir')
    command = 'python manage.py collectstatic -c -l --noinput'
    with fabtools.python.virtualenv(env.virtualenvdir):
        with cd(env.appdir):
            if user:
                with shell_env(HOME=remote_home(user)):
                    sudo(command, user=user)
            else:
                run(command)


def locales(user=None, settings_module=None):
    require('virtualenvdir', 'appdir', 'project_name')
    command = 'python manage.py compilemessages'
    if settings_module:
        settings = settings_module
    else:
        settings = '%s.settings' % env.project_name
    with fabtools.python.virtualenv(env.virtualenvdir):
        with cd(env.appdir):
            if user:
                with shell_env(HOME=remote_home(user),
                               DJANGO_SETTINGS_MODULE=settings):
                    sudo(command, user=user)
            else:
                run(command)
