# -*- coding: utf-8 -*-


from fabric.api import execute
from fabtools import require

from pydiploy import require as dip_require


def application_packages(update=False):
    require.deb.packages(['gettext'], update=update)
    execute(dip_require.database.ldap_pkg, use_sudo=True)
    execute(dip_require.database.postgres_pkg)
    execute(dip_require.python.utils.python_pkg)
    execute(dip_require.circus.circus_pkg)


def pre_install_django_app_nginx_circus(commands='/usr/bin/rsync'):
    execute(dip_require.nginx.root_web)
    execute(dip_require.system.django_user, commands=commands)
    execute(dip_require.system.set_locale)
    execute(dip_require.system.set_timezone)
    execute(dip_require.system.update_pkg_index)
    execute(application_packages)
    execute(dip_require.python.virtualenv.virtualenv)
    execute(dip_require.nginx.nginx_pkg)


def deploy(upgrade_pkg=False, **kwargs):
    """Deploys django webapp"""
    execute(dip_require.releases_manager.setup)
    execute(dip_require.releases_manager.deploy_code)
    execute(dip_require.python.utils.application_dependencies, upgrade_pkg)
    execute(dip_require.django.utils.app_settings, **kwargs)
    execute(dip_require.django.command.django_prepare)
    execute(dip_require.system.permissions)
    execute(dip_require.nginx.nginx_reload)
    execute(dip_require.releases_manager.cleanup)


def rollback():
    """Rollback django webapp"""
    execute(dip_require.releases_manager.rollback_code)
    execute(dip_require.nginx.nginx_reload)


def post_install():
    """Post installation of webapp"""
    execute(dip_require.circus.app_circus_conf)
    execute(dip_require.circus.upstart)
    execute(dip_require.circus.app_reload)
    execute(dip_require.nginx.web_static_files)
    execute(dip_require.nginx.web_configuration)
    execute(dip_require.nginx.nginx_reload)
