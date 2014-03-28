# -*- coding: utf-8 -*-

import fabric
import pydiploy
import fabtools


def application_packages(update=False):
    fabtools.require.deb.packages(['gettext'], update=update)
    fabric.api.execute(pydiploy.require.database.ldap_pkg, use_sudo=True)
    fabric.api.execute(pydiploy.require.database.postgres_pkg)
    fabric.api.execute(pydiploy.require.python.utils.python_pkg)
    fabric.api.execute(pydiploy.require.circus.circus_pkg)


def pre_install_django_app_nginx_circus(commands='/usr/bin/rsync'):
    fabric.api.execute(pydiploy.require.nginx.root_web)
    fabric.api.execute(pydiploy.require.system.django_user, commands=commands)
    fabric.api.execute(pydiploy.require.system.set_locale)
    fabric.api.execute(pydiploy.require.system.set_timezone)
    fabric.api.execute(pydiploy.require.system.update_pkg_index)
    fabric.api.execute(application_packages)
    fabric.api.execute(pydiploy.require.python.virtualenv.virtualenv)
    fabric.api.execute(pydiploy.require.nginx.nginx_pkg)


def deploy(upgrade_pkg=False, **kwargs):
    """Deploys django webapp"""
    fabric.api.execute(pydiploy.require.releases_manager.setup)
    fabric.api.execute(pydiploy.require.releases_manager.deploy_code)
    fabric.api.execute(pydiploy.require.python.utils.application_dependencies, upgrade_pkg)
    fabric.api.execute(pydiploy.require.django.utils.app_settings, **kwargs)
    fabric.api.execute(pydiploy.require.django.command.django_prepare)
    fabric.api.execute(pydiploy.require.system.permissions)
    fabric.api.execute(pydiploy.require.nginx.nginx_reload)
    fabric.api.execute(pydiploy.require.releases_manager.cleanup)


def rollback():
    """Rollback django webapp"""
    fabric.api.execute(pydiploy.require.releases_manager.rollback_code)
    fabric.api.execute(pydiploy.require.nginx.nginx_reload)


def post_install():
    """Post installation of webapp"""
    fabric.api.execute(pydiploy.require.circus.app_circus_conf)
    fabric.api.execute(pydiploy.require.circus.upstart)
    fabric.api.execute(pydiploy.require.circus.app_reload)
    fabric.api.execute(pydiploy.require.nginx.web_static_files)
    fabric.api.execute(pydiploy.require.nginx.web_configuration)
    fabric.api.execute(pydiploy.require.nginx.nginx_reload)