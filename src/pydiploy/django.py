# -*- coding: utf-8 -*-


from fabric.api import env, execute
from fabric.contrib.files import exists
from fabtools import require

from pydiploy import require as dip_require

# def pre_install(tmp_directory, with_settings):
#     require.files.directory(env.remote_workdir)
#     require.files.directory(env.remote_logdir)
#     if with_settings:
#         dip_require.django.settings(tmp_directory)


# def post_install(tmp_directory):
#     dip_require.django.manager(tmp_directory)

#     static_temp = '%s/src/%s/static' % (tmp_directory, env.project_name)
#     if exists(static_temp):
#         dip_require.django.staticfiles(tmp_directory)

#     local_temp = '%s/src/%s/locale' % (tmp_directory, env.project_name)
#     if exists(local_temp):
#         dip_require.django.locale(tmp_directory)
#     require.files.directory(env.django_media_root, use_sudo=True,
#                             owner=env.user, group=env.group)
#
#
# def install(tmp_directory, with_settings=False):
#     pre_install(tmp_directory, with_settings)
#     dip_require.python.install(tmp_directory)
#     post_install(tmp_directory)

def application_packages(update=False):
    require.deb.packages(['gettext'], update=update)
    execute(dip_require.database.ldap_pkg, use_sudo=True)
    execute(dip_require.database.postgres_pkg)
    execute(dip_require.python.utils.python_pkg)
    execute(dip_require.circus.circus_pkg)


def pre_install_django_app_nginx_circus():
    execute(dip_require.nginx.root_web)
    # FIXME -> commands should not be there !!!!
    execute(dip_require.system.django_user,
            commands='/usr/bin/rsync,/usr/sbin/service ipsec restart')
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
    execute(dip_require.circus.app_reload)
    execute(dip_require.nginx.web_static_files)
    execute(dip_require.nginx.web_configuration)
    execute(dip_require.nginx.nginx_reload)
