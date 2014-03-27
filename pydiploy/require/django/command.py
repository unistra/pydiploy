# -*- coding: utf-8 -*-

"""
"""

import os
import fabric
from fabric.api import env
import fabtools


def django_prepare():
    with fabtools.python.virtualenv(env.remote_virtualenv_dir):
        with fabric.api.cd(env.remote_current_path):
            with fabric.api.settings(sudo_user=env.remote_owner):
                fabric.api.sudo('python manage.py syncdb --noinput')
                fabric.api.sudo('python manage.py migrate')
                if fabtools.files.is_dir(
                    os.path.join(env.remote_base_package_dir,
                                 'locale')):
                    fabric.api.sudo('python manage.py compilemessages')
                ignore = ('admin',  'rest_framework',  'django_extensions')
                fabric.api.sudo('python manage.py collectstatic --noinput -i %s' %
                     ' -i '.join(ignore))
    fabric.api.get(os.path.join(env.remote_current_path, 'assets'),
        local_path=env.local_tmp_dir)
