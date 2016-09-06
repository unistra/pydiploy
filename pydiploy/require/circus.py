# -*- coding: utf-8 -*-

"""

Methods to install circus package



.. seealso::

    `circus documentation <http://circus.readthedocs.org>`_
      Circus official documentation.

"""

import os

import fabric
import fabtools
from fabric.api import env, warn_only
from pydiploy.decorators import do_verbose
from .system import is_systemd


@do_verbose
def circus_pkg(update=False):
    """ Installs packages relatives to circus """

    # install ubuntu ppa for libzmq-dev if ubuntu <= 10.04
    if fabtools.system.distrib_id() == 'Ubuntu' and fabtools.system.distrib_release() == '10.04':
        fabtools.require.deb.packages(['python-software-properties'],
                                      update=update)
        fabtools.require.deb.ppa('ppa:chris-lea/zeromq')
        fabtools.require.deb.ppa('ppa:chris-lea/libpgm')

    fabtools.require.deb.packages([
        'libzmq-dev',
        'libevent-dev'], update=update)
    # not used anymore installed in venv !
    fabtools.require.python.install(env.get('circus_package_name', 'circus'),
                                    use_sudo=True, upgrade=update)

    if 'no_circus_web' not in env or not env.no_circus_web:
        fabtools.require.python.install('circus-web', use_sudo=True, upgrade=update)
        fabtools.require.python.install('gevent', use_sudo=True, upgrade=update)

    # install circus backend sets in fabfile
    if 'circus_backend' in env:
        fabtools.require.python.install(env.circus_backend, use_sudo=True, upgrade=update)

    # base configuration file for circus
    fabtools.files.upload_template(
        'circus.ini.tpl',
        os.path.join(env.remote_home,
                     '.circus.ini'),
        context=env,
        template_dir=os.path.join(env.lib_path, 'templates'),
        use_sudo=True,
        user=env.remote_owner,
        chown=True,
        mode='644',
        use_jinja=True)

    # root directory for circus applications configuration
    fabtools.require.files.directory(
        path=os.path.join(env.remote_home, '.circus.d'),
        use_sudo=True,
        owner=env.remote_owner,
        group=env.remote_group,
        mode='750')


@do_verbose
def app_circus_conf():
    """
    Sets circus app's configuration using templates in templates dir
    """

    fabtools.files.upload_template('app.ini.tpl',
                                   os.path.join(env.remote_home, '.circus.d',
                                                '%s.ini' % env.application_name),
                                   context=env,
                                   template_dir=os.path.join(
                                       env.lib_path, 'templates'),
                                   use_sudo=True,
                                   user=env.remote_owner,
                                   chown=True,
                                   mode='644',
                                   use_jinja=True)


@do_verbose
def upstart():
    """
    Sets script to start circus at boot using templates in templates dir
    """
    # Systemd
    if is_systemd():
        # init files to declare circus as a systemd daemon
        fabtools.files.upload_template('circus.service.tpl',
                                       '/etc/systemd/system/circus.service',
                                       context=env,
                                       template_dir=os.path.join(
                                           env.lib_path, 'templates'),
                                       use_sudo=True,
                                       user='root',
                                       chown=True,
                                       mode='644',
                                       use_jinja=True)
        fabric.api.sudo('systemctl daemon-reload')
    # Upstart
    else:
        # init files to declare circus as an upstart daemon
        fabtools.files.upload_template('upstart.conf.tpl',
                                       '/etc/init/circus.conf',
                                       context=env,
                                       template_dir=os.path.join(
                                           env.lib_path, 'templates'),
                                       use_sudo=True,
                                       user='root',
                                       chown=True,
                                       mode='644',
                                       use_jinja=True)


@do_verbose
def app_reload():
    """ Starts/restarts app using circus """

    # Systemd
    if is_systemd():
        start_cmd = 'systemctl start circus.service'
        status_cmd = 'systemctl is-active circus.service'
        with warn_only():
            running = 'inactive' not in fabric.api.sudo(status_cmd)
    # Upstart
    else:
        start_cmd = 'start circus'
        status_cmd = 'status circus'
        running = 'running' in fabric.api.sudo(status_cmd)

    if not running:
        fabric.api.sudo(start_cmd)
    else:
        with fabric.api.settings(sudo_user=env.remote_owner):
            fabric.api.sudo('circusctl reloadconfig')
            fabric.api.sudo('circusctl restart %s' % env.application_name)
