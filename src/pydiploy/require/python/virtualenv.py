# -*- coding: utf-8 -*-

"""
"""

import os
from fabric.api import env
import fabtools
from pydiploy.system import remote_home


def virtualenv(virtualenv_name, python_version, user, group):
    """
    """
    env.virtualenvdir = os.path.join(virtualenvs_directory(user),
            virtualenv_name)
    fabtools.require.python.virtualenv(
        env.virtualenvdir, python='/usr/bin/python%s' % python_version,
        user=user, group=group, use_sudo=True, mode=755
    )


def virtualenvs_directory(user, group):
    """
    """
    home_directory = remote_home(user)
    venv_path = os.path.join(home_directory, '.virtualenvs')
    fabtools.require.directory(venv_path, user=user, group=group,
            use_sudo=True)
    return venv_path
