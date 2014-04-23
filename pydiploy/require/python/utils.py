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
        '%s' % 'python-dev' if env.remote_python_version < 3 else 'python%s-dev' % env.remote_python_version,
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
            pip_cmd = 'pip'
            if 'oracle_client_version' in env:
                oracle_dir = 'instantclient_%s' % '_'.join(
                    env.oracle_client_version.split('.')[:2])
                oracle_root_path = os.path.join(
                    env.oracle_remote_dir, oracle_dir)
                oracle_full_path = os.path.join(
                    env.remote_home, oracle_root_path)
                pip_cmd = 'ORACLE_HOME=%s pip' % oracle_full_path

            fabtools.python.install_requirements(requirements_file,
                                                 use_sudo=True,
                                                 user=env.remote_owner,
                                                 upgrade=upgrade_pkg,
                                                 pip_cmd=pip_cmd)

            fabric.api.sudo(
                'pip install -e .', user=env.remote_owner, pty=False)
