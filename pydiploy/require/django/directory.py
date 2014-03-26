# -*- coding: utf-8 -*-

"""
"""

import os

from fabric.api import cd, env, get, put, require, run
import fabtools

from ...system import remote_home


def media(user, group):
    require('virtualhost')
    if not env.has_key('django_media_root'):
        env.django_media_root = os.path.join(os.path.sep, 'var', 'www', 'data',
                                             env.virtualhost)
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


def static(user, group):
    """
    """
    require('virtualhost', 'appdir')
    if not env.has_key('django_static_root'):
        env.django_static_root = os.path.join(env.appdir, 'static')
        fabtools.require.files.directory(env.django_static_root, use_sudo=True,
                                         owner=user, group=group, mode='755')
    return env.django_static_root
