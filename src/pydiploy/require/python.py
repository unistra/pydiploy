# -*- coding: utf-8 -*-

"""
"""

import os

from fabric.api import env
from fabric.api import cd
from fabric.api import run
from fabric.contrib.files import exists

import fabtools
from fabtools import require


def install(tmp_directory):
    """
    """
    require.python.distribute()
    require.python.pip(version='dev')
    with fabtools.python.virtualenv(env.virtualenv_dir):
        with cd(tmp_directory):
            run('python setup.py install')
            if exists('requirements/%s.txt' % env.env):
                require.python.requirements('requirements/%s.txt' % env.env)


def virtualenv(virtualenv_name, python_version, user):
    """
    """
    require.python.virtualenv(
            os.path.join(virtualenvs_directory(user), virtualenv_name),
            python='/usr/bin/python%s' % python_version,
            user=user, use_sudo=True)


def virtualenvs_directory(user):
    """
    """
    user_info = run('cat /etc/passwd |grep %s' % user)
    home_directory = user_info.split(':')[5]
    venv_path = os.path.join(home_directory, '.virtualenvs')
    require.directory(venv_path)
    return venv_path


def pypirc(local_name, local_uri, local_user, local_password,
        system_user, system_group):
    """
    """
    user_info = run('cat /etc/passwd |grep %s' % system_user)
    home_directory = user_info.split(':')[5]
    fabtools.require.files.template_file(
            path=os.path.join(home_directory, '.pypirc'),
            template_contents=PYPIRC, context=locals(),
            mode='755', owner=system_user, group=system_group,
            use_sudo=True
    )


PYPIRC = """\
[distutils]
index-servers = 
    pypi
    %(local_name)s

[pypi]
repository: https://pypi.python.org/simple/

[%(local_name)s]
repository: %(local_uri)s
username: %(local_user)s
password: %(local_password)s
"""
