# -*- coding: utf-8 -*-

""" This module is used for commands relatives to django framework

"""

import datetime
import os

import fabric
import fabtools
from fabric.api import env
from pydiploy.decorators import do_verbose
from distutils.version import LooseVersion


@do_verbose
def django_prepare():
    """
    Prepares django webapp (syncdb,migrate,collectstatic,and eventually
    compilemessages)
    """

    # remove old statics from local tmp dir before collecting new ones
    with fabric.api.lcd(env.local_tmp_dir):
        fabric.api.local('rm -rf assets/*')
    # TODO refactoring using django_get_version && django_custom_cmd
    with fabtools.python.virtualenv(env.remote_virtualenv_dir):
        with fabric.api.cd(env.remote_current_path):
            with fabric.api.settings(sudo_user=env.remote_owner):
                # django_version = fabric.api.sudo(
                #     'python -c "import django;print(django.get_version())"')
                # check if django >= 1.8 no more syncdb migrate only !
                if LooseVersion(django_get_version()) < LooseVersion("1.8"):
                    fabric.api.sudo('python manage.py syncdb --noinput')
                # TODO add point in documentation
                # south needed with django < 1.7 !!!!!
                with fabric.api.settings(warn_only=True):
                    fabric.api.sudo('python manage.py migrate')
                    fabric.api.sudo('python manage.py compilemessages')
                # ignore = ('rest_framework',  'django_extensions')
                # fabric.api.sudo('python manage.py collectstatic --noinput -i %s' %
                #                 ' -i '.join(ignore))
                fabric.api.sudo('python manage.py collectstatic --noinput')

    fabric.api.get(os.path.join(env.remote_current_path, 'assets'),
                   local_path=env.local_tmp_dir)


@do_verbose
def django_dump_database():
    """
    Dumps webapp datas in json.

    If env.dest_path is not set in fabfile or --set dest_path is not
    used in command line uses default /tmp in local machine using the
    fabfile.

    """
    with fabtools.python.virtualenv(env.remote_virtualenv_dir):
        with fabric.api.cd(env.remote_current_path):
            with fabric.api.settings(sudo_user=env.remote_owner):
                dump_name = '%s.json' % datetime.datetime.today().strftime(
                    "%Y_%m_%d-%H%M")
                fabric.api.sudo(
                    'python manage.py dumpdata --indent=4 > /tmp/%s ' % dump_name)
    fabric.api.get('/tmp/%s' % dump_name, local_path=env.dest_path)


@do_verbose
def django_custom_cmd(commands):
    """ Passes custom commands to manage.py """

    with fabtools.python.virtualenv(env.remote_virtualenv_dir):
        with fabric.api.cd(env.remote_current_path):
            with fabric.api.settings(sudo_user=env.remote_owner):
                fabric.api.sudo('python manage.py %s' % commands)


@do_verbose
def django_get_version():
    """ Gets django version on remote """

    # hopefully never compare with django_version=0 :)
    django_version = 0
    
    with fabtools.python.virtualenv(env.remote_virtualenv_dir):
        with fabric.api.cd(env.remote_current_path):
            with fabric.api.settings(sudo_user=env.remote_owner):
                django_version = fabric.api.sudo(
                    'python -c "import django;print(django.get_version())"')

                return django_version
