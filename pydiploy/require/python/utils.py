# -*- coding: utf-8 -*-
import os
import fabtools
import fabric
from fabric.api import env


def python_pkg(update=False):
    """
    Installs python packages and pip
    """
    fabtools.require.deb.packages([
        'python-dev',
        'python-pip'
    ], update=update)
    fabtools.require.python.install('pip', upgrade=True, use_sudo=True)


def application_dependencies(upgrade_pkg, staging=True):
    """
    Installs application dependencies with requirements.txt files
    """
    with fabtools.python.virtualenv(env.remote_virtualenv_dir):
        with fabric.api.cd(env.remote_current_path):
            requirements_file = os.path.join('requirements',
                                             '%s.txt' % env.goal) if staging else 'requirements.txt'

            fabtools.python.install_requirements(requirements_file,
                                                 use_sudo=True,
                                                 user=env.remote_owner,
                                                 upgrade=upgrade_pkg)

            fabric.api.sudo('pip install -e .', user=env.remote_owner, pty=False)
