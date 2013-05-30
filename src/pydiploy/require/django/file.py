"""
"""

import os


from fabric.api import cd
from fabric.api import env
from fabric.api import get
from fabric.api import put
from fabric.api import require
from fabric.context_managers import settings
import fabtools

from ...system import remote_home
from .directory import local_settings


def manager(remote_user, template_path):
    """
    """
    require('appdir')
    fabtools.require.files.template_file(
            path=os.path.join(env.appdir, 'manage.py'), 
            template_source=template_path, context=env, 
            use_sudo=True, owner=remote_user
    )


def log(app_name):
    """
    """
    require('logdir')
    if not env.has_key('django_logile'):
        env.django_logfile = os.path.join(env.logdir, '%s.log' % app_name)
    return env.django_logfile


def settings(remote_user, template_path):
    """
    """
    require('project_name')
    local_path = local_settings(remote_user)
    fabtools.require.files.template_file(
        path=os.path.join(local_path, 'conf.py'),
        template_source=template_path, context=env, use_sudo=True,
        owner=remote_user
    )
