# -*- coding: utf-8 -*-

"""
"""

import os

from fabric.api import (cd, env, get, put, require, run, sudo, shell_env,
                        settings)
import fabtools

from ...system import remote_home


def django_prepare():
    with fabtools.python.virtualenv(env.remote_virtualenv_dir):
        with cd(env.remote_current_path):
            with settings(sudo_user=env.remote_owner):
                sudo('python manage.py syncdb --noinput')
                sudo('python manage.py migrate')
                if fabtools.files.is_dir(
                    os.path.join(env.remote_base_package_dir,
                                 'locale')):
                    sudo('python manage.py compilemessages')
                ignore = ('admin',  'rest_framework',  'django_extensions')
                sudo('python manage.py collectstatic --noinput -i %s' %
                     ' -i '.join(ignore))
    get(os.path.join(env.remote_current_path, 'assets'),
        local_path=env.local_tmp_dir)
