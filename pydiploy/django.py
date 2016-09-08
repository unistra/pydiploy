# -*- coding: utf-8 -*-

""" This module is used to deploy a whole django webapp using chaussette/circus nginx on a remote/vagrant machine.

This module shoud be imported in a fabfile to deploy an application using pydiploy.

"""


from contextlib import contextmanager

import fabric
import fabtools
import pydiploy
from fabric.api import env
from pydiploy.decorators import do_verbose


@contextmanager
def wrap_deploy():
    try:
        yield
    except SystemExit:
        fabric.api.execute(rollback)
        fabric.api.abort(fabric.colors.red(
            "Deploy failed rollbacking process launched"))


@do_verbose
def application_packages(update=False):
    """ Installs all packages for django webapp """
    fabtools.require.deb.packages(['gettext'], update=update)

    if env.remote_python_version >= 3:
        fabric.api.execute(pydiploy.require.system.check_python3_install,
                           version='python%s' % env.remote_python_version)
    fabric.api.execute(pydiploy.require.python.utils.python_pkg)
    if env.has_key('extra_ppa_to_install'):
        fabric.api.execute(
            pydiploy.require.system.install_extra_ppa, env.extra_ppa_to_install)
    if env.has_key('extra_source_to_install'):
        fabric.api.execute(
            pydiploy.require.system.install_extra_source, env.extra_source_to_install)
    if env.has_key('extra_pkg_to_install'):
        fabric.api.execute(
            pydiploy.require.system.install_extra_packages, env.extra_pkg_to_install)


def pre_install_backend(commands='/usr/bin/rsync', upgrade_circus=False):
    """ Installs requirements for circus & virtualenv env """
    fabric.api.execute(pydiploy.require.system.add_user, commands=commands)
    fabric.api.execute(pydiploy.require.system.set_locale)
    fabric.api.execute(pydiploy.require.system.set_timezone)
    fabric.api.execute(pydiploy.require.system.update_pkg_index)
    fabric.api.execute(application_packages)
    fabric.api.execute(pydiploy.require.circus.circus_pkg, update=upgrade_circus)
    fabric.api.execute(pydiploy.require.python.virtualenv.virtualenv)
    fabric.api.execute(pydiploy.require.circus.upstart)


def pre_install_frontend():
    """ Installs requirements for nginx """
    fabric.api.execute(pydiploy.require.nginx.root_web)
    fabric.api.execute(pydiploy.require.system.update_pkg_index)
    fabric.api.execute(pydiploy.require.nginx.nginx_pkg)


def deploy_backend(upgrade_pkg=False, **kwargs):
    """ Deploys django webapp with required tag """
    with wrap_deploy():
        fabric.api.execute(pydiploy.require.releases_manager.setup)
        fabric.api.execute(pydiploy.require.releases_manager.deploy_code)
        fabric.api.execute(pydiploy.require.django.utils.deploy_manage_file)
        fabric.api.execute(pydiploy.require.django.utils.deploy_wsgi_file)
        fabric.api.execute(
            pydiploy.require.python.utils.application_dependencies,
            upgrade_pkg)
        fabric.api.execute(pydiploy.require.django.utils.app_settings,
            **kwargs)
        fabric.api.execute(pydiploy.require.django.command.django_prepare)
        fabric.api.execute(pydiploy.require.system.permissions)
        fabric.api.execute(pydiploy.require.circus.app_reload)
        fabric.api.execute(pydiploy.require.releases_manager.cleanup)


def deploy_frontend():
    """ Synchronises static files after deploy """
    fabric.api.execute(pydiploy.require.nginx.web_static_files)


def rollback():
    """ Rolls back django webapp """
    fabric.api.execute(pydiploy.require.releases_manager.rollback_code)
    fabric.api.execute(pydiploy.require.circus.app_reload)


def post_install_backend():
    """ Post-installation of webapp"""
    fabric.api.execute(pydiploy.require.circus.app_circus_conf)
    fabric.api.execute(pydiploy.require.circus.app_reload)


def post_install_frontend():
    fabric.api.execute(pydiploy.require.nginx.web_configuration)
    fabric.api.execute(pydiploy.require.nginx.nginx_restart)


def dump_database():
    """ Dumps database in json """
    fabric.api.execute(pydiploy.require.django.command.django_dump_database)


def reload_frontend():
    """ Reloads frontend """
    fabric.api.execute(pydiploy.require.nginx.nginx_reload)


def reload_backend():
    """ Reloads backend """
    fabric.api.execute(pydiploy.require.circus.app_reload)


def set_app_down():
    """ Sets app in maintenance mode """
    fabric.api.execute(pydiploy.require.nginx.down_site_config)
    fabric.api.execute(pydiploy.require.nginx.set_website_down)


def set_app_up():
    """ Sets app up """
    fabric.api.execute(pydiploy.require.nginx.set_website_up)


def custom_manage_command(cmd):
    """ Passes custom commandes to manage.py """
    fabric.api.execute(pydiploy.require.django.command.django_custom_cmd, cmd)


def install_postgres_server(user=None,dbname=None,password=None):
    """ Install postgres server & add user for postgres

        if no parameters are provided using (if exists) ::

            default_db_user
            default_db_name
            default_db_password

    """

    if not (user and dbname and password):
        if all([e in env.keys() for e in ('default_db_user', 'default_db_name', 'default_db_password')]):
            user = env.default_db_user
            dbname = env.default_db_name
            password = env.default_db_password
        else:
            fabric.api.abort('Please provide user,dbname,password parameters for postgres.')

    fabric.api.execute(pydiploy.require.databases.postgres.install_postgres_server)
    fabric.api.execute(pydiploy.require.databases.postgres.add_postgres_user,user,password=password)
    fabric.api.execute(pydiploy.require.databases.postgres.add_postgres_database,dbname,owner=user,locale=env.locale)


def install_oracle_client():
    """ Install oracle client. """
    fabric.api.execute(pydiploy.require.databases.oracle.install_oracle_client)


def install_sap_client():
    """ Install saprfc bindings to an SAP instance. """
    fabric.api.execute(pydiploy.require.databases.sap.install_sap_client)
