# -*- coding: utf-8 -*-
import os
import fabtools

from fabric.api import env, cd, sudo


def python_pkg(update=False):
    fabtools.require.deb.packages([
        'python-dev',
        'python-pip'
    ], update=update)
    fabtools.require.python.install('pip', upgrade=True, use_sudo=True)


def application_dependencies(upgrade_pkg):
    with fabtools.python.virtualenv(env.remote_virtualenv_dir):
        with cd(env.remote_current_path):
            fabtools.python.install_requirements(os.path.join('requirements',
                                                              '%s.txt' % env.goal),
                                                 use_sudo=True,
                                                 user=env.remote_owner,
                                                 upgrade=upgrade_pkg)
            sudo('pip install -e .', user=env.remote_owner, pty=False)
