# -*- coding: utf-8 -*-

"""
Circus
======

.. circus: http://circus.readthedocs.org
"""

import os
from fabric.api import env, sudo, settings
import fabtools


def circus_pkg(update=False):
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
    fabtools.require.python.install('gevent', use_sudo=True)
    fabtools.require.python.install('circus', use_sudo=True)
    fabtools.require.python.install('circus-web', use_sudo=True)

    # base configuration file for circus

    CIRCUS_BASE_CONFIG = """\
[circus]
httpd = 1
httpd_host = %(host)s
httpd_port = 8080
stream_backend = gevent
statsd = 1
pidfile = %(remote_home)s/.circus.pid
include_dir = %(remote_home)s/.circus.d
    """
    fabtools.require.files.template_file(path=os.path.join(
                                         env.remote_home, '.circus.ini'),
                                         template_contents=CIRCUS_BASE_CONFIG,
                                         context=env,
                                         use_sudo=True,
                                         owner=env.remote_owner,
                                         group=env.remote_group,
                                         mode='644')

    # root directory for circus applications configuration
    fabtools.require.files.directory(
        path=os.path.join(env.remote_home, '.circus.d'),
        use_sudo=True,
        owner=env.remote_owner,
        group=env.remote_group,
        mode='750')


def app_circus_conf():
    """
    """

    CIRCUS_APP_CONFIG = """\
[watcher:%(application_name)s]
cmd = %(remote_virtualenv_dir)s/bin/chaussette --fd $(circus.sockets.%(application_name)s) %(root_package_name)s.wsgi.application
working_dir = %(remote_current_path)s
copy_env = 1
numprocesses = 3
use_sockets = 1
virtualenv = %(remote_virtualenv_dir)s
uid = django
gid = di

stderr_stream.class = FileStream
stdout_stream.filename = %(remote_shared_path)s/log/circus_error.log
stdout_stream.time_format = %%Y-%%m-%%d %%H:%%M:%%S
stdout_stream.max_bytes = 209715200
stdout_stream.backup_count = 5

stdout_stream.class = FileStream
stdout_stream.filename = %(remote_shared_path)s/log/circus.log
stdout_stream.time_format = %%Y-%%m-%%d %%H:%%M:%%S
stdout_stream.max_bytes = 209715200
stdout_stream.backup_count = 5

[socket:%(application_name)s]
host = %(socket_host)s
port = %(socket_port)s
    """

    fabtools.require.files.template_file(
        path=os.path.join(env.remote_home, '.circus.d',
                          'cmscts.ini'),
        template_contents=CIRCUS_APP_CONFIG,
        context=env,
        use_sudo=True,
        owner=env.remote_owner,
        group=env.remote_group,
        mode='644')


def upstart():
    """
    """

    UPSTART_CONFIG = """\
start on filesystem and net-device-up IFACE=lo

stop on started shutdown

respawn
exec /usr/local/bin/circusd %(remote_home)s/.circus.ini
    """

    fabtools.require.files.template_file(
        path='/etc/init/circus.conf',
        template_contents=UPSTART_CONFIG,
        context=env,
        use_sudo=True,
        owner='root',
        mode='644')


def app_reload():
    """Start/Restart app using circus"""
    if not 'running' in sudo('status circus'):
        sudo('start circus')
    else:
        with settings(sudo_user=env.remote_owner):
            sudo('circusctl restart %s' % env.application_name)
