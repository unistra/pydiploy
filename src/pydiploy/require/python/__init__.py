import os
import fabtools
from fabric.api import env
from . import environnment
from . import directory
from ...system import remote_home


def virtualenv(virtualenv_name, python_version, user, group):
    """
    """
    env.virtualenvdir = os.path.join(virtualenvs_directory(user, group),
            virtualenv_name)
    fabtools.require.python.virtualenv(
        env.virtualenvdir, python='/usr/bin/python%s' % python_version,
        user=user, use_sudo=True
    )


def virtualenvs_directory(user, group):
    """
    """
    home_directory = remote_home(user)
    venv_path = os.path.join(home_directory, '.virtualenvs')
    fabtools.require.directory(venv_path, owner=user, group=group,
            use_sudo=True)
    return venv_path
