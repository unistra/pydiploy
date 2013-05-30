"""
"""

import os

from fabric.api import cd
from fabric.api import env
from fabric.api import get
from fabric.api import put
from fabric.api import require
from fabric.api import run

import fabtools

from ...system import remote_home


def media(user, group, app_name):
    if not env.has_key('django_media_root'):
        env.django_media_root = os.path.join(os.path.sep, 'var', 'www', 'data',
                app_name)
        fabtools.require.files.directory(env.django_media_root, use_sudo=True,
                owner=user, group=group, mode='755')
    return env.django_media_root


def local_settings(user):
    """
    """
    require('project_name')
    local_path = os.path.join(remote_home(user), '.%s' % env.project_name)
    fabtools.require.files.directory(local_path, use_sudo=True, owner=user,
            mode='755')
    return local_path
