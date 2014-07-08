# -*- coding: utf-8 -*-

"""
    This module is used to deploy a whole django webapp on a remote/vagrant machine :

"""


import fabric
import pydiploy
import fabtools

from fabric.api import env


def application_packages(update=False):
    """ Installs all packages for django webapp """
    fabtools.require.deb.packages(['gettext'], update=update)
    # TODO contextual installation of ldap packages & postgres packages !!!
    fabric.api.execute(pydiploy.require.database.ldap_pkg, use_sudo=True)
    fabric.api.execute(pydiploy.require.database.postgres_pkg)
    if env.remote_python_version >= 3:
        fabric.api.execute(pydiploy.require.system.check_python3_install,
                           version='python%s' % env.remote_python_version)
    fabric.api.execute(pydiploy.require.python.utils.python_pkg)


def pre_install_backend(commands='/usr/bin/rsync'):
    """ Installs requirements for circus & virtualenv env """
    fabric.api.execute(pydiploy.require.system.django_user, commands=commands)
    fabric.api.execute(pydiploy.require.system.set_locale)
    fabric.api.execute(pydiploy.require.system.set_timezone)
    fabric.api.execute(pydiploy.require.system.update_pkg_index)
    fabric.api.execute(application_packages)
    fabric.api.execute(pydiploy.require.circus.circus_pkg)
    fabric.api.execute(pydiploy.require.python.virtualenv.virtualenv)
    fabric.api.execute(pydiploy.require.circus.upstart)


def pre_install_frontend(commands='/usr/bin/rsync'):
    """ Installs requirements for nginx """
    fabric.api.execute(pydiploy.require.nginx.root_web)
    fabric.api.execute(pydiploy.require.system.update_pkg_index)
    fabric.api.execute(pydiploy.require.nginx.nginx_pkg)


def deploy(upgrade_pkg=False, **kwargs):
    """ Deploys django webapp with required tag """
    fabric.api.execute(pydiploy.require.releases_manager.setup)
    fabric.api.execute(pydiploy.require.releases_manager.deploy_code)
    fabric.api.execute(
        pydiploy.require.python.utils.application_dependencies, upgrade_pkg)
    fabric.api.execute(pydiploy.require.django.utils.app_settings, **kwargs)
    fabric.api.execute(pydiploy.require.django.command.django_prepare)
    fabric.api.execute(pydiploy.require.system.permissions)
    fabric.api.execute(pydiploy.require.circus.app_reload)
    fabric.api.execute(pydiploy.require.releases_manager.cleanup)


def rollback():
    """ Rolls back django webapp """
    fabric.api.execute(pydiploy.require.releases_manager.rollback_code)
    fabric.api.execute(pydiploy.require.circus.app_reload)


def post_install_backend():
    """ Post installation of webapp"""
    fabric.api.execute(pydiploy.require.circus.app_circus_conf)
    fabric.api.execute(pydiploy.require.circus.app_reload)


def post_install_frontend():
    fabric.api.execute(pydiploy.require.nginx.web_static_files)
    fabric.api.execute(pydiploy.require.nginx.web_configuration)
    fabric.api.execute(pydiploy.require.nginx.nginx_restart)


def dump_database():
    """ Dumps database in json """
    fabric.api.execute(pydiploy.require.django.command.django_dump_database)


def reload_frontend():
    """ Reload frontend """
    fabric.api.execute(pydiploy.require.nginx.nginx_reload)


def reload_backend():
    """ Reload backend """
    fabric.api.execute(pydiploy.require.circus.app_reload)
