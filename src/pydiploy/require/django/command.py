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

import fabtools


def staticfiles(user=None):
    require('virtualenvdir', 'appdir')
    command = 'python manage.py collectstatic -c -l --noinput'
    env.django_static_root = os.path.join(env.appdir, 'static')
    with fabtools.python.virtualenv(env.virtualenvdir):
        with cd(env.appdir):
            if user:
                sudo(command, user=user)
            else:
                run(command)


def locales(user=None):
    require('virtualenvdir', 'appdir')
    command = 'python manage.py compilemessages'
    with fabtools.python.virtualenv(env.virtualenvdir):
        with cd(env.appdir):
            if user:
                sudo(command, user=user)
            else:
                run(command)
