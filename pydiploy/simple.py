# -*- coding: utf-8 -*-
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
    """ Installs all packages for the app """
    fabtools.require.deb.packages(['gettext'], update=update)
    if env.remote_python_version >= 3:
        fabric.api.execute(pydiploy.require.system.check_python3_install,
                           version='python%s' % env.remote_python_version)
    fabric.api.execute(pydiploy.require.python.utils.python_pkg)
    if 'extra_ppa_to_install' in env:
        fabric.api.execute(
            pydiploy.require.system.install_extra_ppa,
            env.extra_ppa_to_install)
    if 'extra_source_to_install' in env:
        fabric.api.execute(
            pydiploy.require.system.install_extra_source,
            env.extra_source_to_install)
    if 'extra_pkg_to_install' in env:
        fabric.api.execute(
            pydiploy.require.system.install_extra_packages,
            env.extra_pkg_to_install)


def pre_install_backend(commands='/usr/bin/rsync'):
    """ Installs requirements for virtualenv env """
    fabric.api.execute(pydiploy.require.system.add_user, commands=commands)
    fabric.api.execute(pydiploy.require.system.set_locale)
    fabric.api.execute(pydiploy.require.system.set_timezone)
    fabric.api.execute(pydiploy.require.system.update_pkg_index)
    fabric.api.execute(application_packages)
    fabric.api.execute(pydiploy.require.python.virtualenv.virtualenv)


def deploy_backend(upgrade_pkg=False, **kwargs):
    """Deploy code on server"""
    with wrap_deploy():
        fabric.api.execute(pydiploy.require.releases_manager.setup)
        fabric.api.execute(pydiploy.require.releases_manager.deploy_code)
        fabric.api.execute(
            pydiploy.require.python.utils.application_dependencies,
            upgrade_pkg)
        # TODO PUT THIS METHOD IN OTHER PACKAGE
        fabric.api.execute(pydiploy.require.simple.utils.app_settings,
                           **kwargs)
        fabric.api.execute(pydiploy.require.simple.utils.deploy_environ_file)
        fabric.api.execute(pydiploy.require.system.permissions)
        fabric.api.execute(pydiploy.require.releases_manager.cleanup)


def post_install_backend():
    """ Post installation of backend. """
    pass





def rollback():
    """ Rollback code (current-1 release). """
    fabric.api.execute(pydiploy.require.releases_manager.rollback_code)
