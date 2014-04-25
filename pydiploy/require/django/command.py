# -*- coding: utf-8 -*-

"""
"""

import os
import fabric
import datetime
from fabric.api import env
import fabtools


def django_prepare():
    """
    Prepares django webapp (syncdb,migrate,collectstatic,and eventually compilemessages)
    """
    with fabtools.python.virtualenv(env.remote_virtualenv_dir):
        with fabric.api.cd(env.remote_current_path):
            with fabric.api.settings(sudo_user=env.remote_owner):
                fabric.api.sudo('python manage.py syncdb --noinput')
                # TODO add point in documentation
                # south needed with django < 1.7 !!!!!
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


def django_dump_database():
    """
    Dumps webapp datas in json
    """
    with fabtools.python.virtualenv(env.remote_virtualenv_dir):
        with fabric.api.cd(env.remote_current_path):
            with fabric.api.settings(sudo_user=env.remote_owner):
                dump_name = '%s.json' % datetime.datetime.today().strftime(
                    "%Y_%m_%d-%H%M")
                fabric.api.sudo(
                    'python manage.py dumpdata --indent=4 > /tmp/%s ' % dump_name)
    fabric.api.get('/tmp/%s' % dump_name, local_path=env.dest_path)
