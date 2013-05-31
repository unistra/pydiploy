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


def manager(template_path, remote_user=None):
    """
    """
    require('appdir')
    kwargs = remote_user and {'use_sudo': True, 'owner': remote_user} or {}
    fabtools.require.files.template_file(
            path=os.path.join(env.appdir, 'manage.py'), 
            template_source=template_path, context=env, 
            **kwargs
    )


def log():
    """
    """
    require('logdir', 'project_name')
    if not env.has_key('django_logile'):
        env.django_logfile = os.path.join(
                env.logdir, '%s.log' % env.project_name
        )
    return env.django_logfile


def settings(template_path, remote_user=None):
    """
    """
    require('project_name')
    local_path = local_settings(remote_user)
    kwargs = remote_user and {'use_sudo': True, 'owner': remote_user} or {}
    fabtools.require.files.template_file(
        path=os.path.join(local_path, 'conf.py'),
        template_source=template_path, context=env, **kwargs
    )
