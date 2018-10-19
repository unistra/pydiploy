# -*- coding: utf-8 -*-

""" Utilities module for python """

import os

import fabric
import fabtools
from fabric.api import env
from pydiploy.decorators import do_verbose
from pydiploy.require.system import shell


@do_verbose
def python_pkg(update=False):
    """ Installs python packages and pip """

    fabtools.require.deb.packages([
        '%s' % 'python-dev' if env.remote_python_version < 3 else 'python%s-dev' % env.remote_python_version,
        'python-pip'
    ], update=update)
    fabtools.require.python.install('pip', upgrade=True, use_sudo=True)


@do_verbose
def application_dependencies(upgrade_pkg, staging=True):
    """ Installs application dependencies with requirements.txt files """

    with fabtools.python.virtualenv(env.remote_virtualenv_dir):
        with fabric.api.cd(env.remote_current_path):
            requirements_file = os.path.join('requirements',
                                             '%s.txt' % env.goal) if staging else 'requirements.txt'
            # ugly fix for error when pip install fail and error raises while /home/user/.pip not writable
            pip_log = '%s/pip_error.log' % env.remote_home
            pip_cmd = 'pip --log-file %s' % pip_log
            if 'oracle_client_version' in env:
                oracle_dir = 'instantclient_%s' % '_'.join(
                    env.oracle_client_version.split('.')[:2])
                oracle_root_path = os.path.join(
                    env.oracle_remote_dir, oracle_dir)
                oracle_full_path = os.path.join(
                    env.remote_home, oracle_root_path)
                pip_cmd = 'ORACLE_HOME=%s pip' % oracle_full_path

            with shell("HOME=~%s %s" % (env.remote_owner, env.shell)):
                # upgrade pip to latest version
                fabtools.require.python.install('pip',
                                                upgrade=True,
                                                use_sudo=True,
                                                user=env.remote_owner,
                                                pip_cmd=pip_cmd,
                                                quiet=True)

                fabtools.python.install_requirements(requirements_file,
                                                 use_sudo=True,
                                                 user=env.remote_owner,
                                                 upgrade=upgrade_pkg,
                                                 pip_cmd='%s --no-cache-dir' % pip_cmd,
                                                 quiet=True)

                fabric.api.sudo(
                    'pip install --log-file %s --quiet -e .' % pip_log ,
                    user=env.remote_owner,
                    pty=False)
