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
    # fabtools.require.python.install('gevent', use_sudo=True)
    fabtools.require.python.install('circus', use_sudo=True)
    fabtools.require.python.install('circus-web', use_sudo=True)

    # base configuration file for circus

    APP_INI_FILE = """\
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
                                         template_contents=APP_INI_FILE,
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

    CIRCUS_INI_FILE = """\
    [watcher:{{ application_name }}]
    cmd = {{ remote_virtualenv_dir }}/bin/chaussette --fd $(circus.sockets.{{ application_name }}) {{ root_package_name }}.wsgi.application
    working_dir = {{ remote_current_path }}
    copy_env = 1
    numprocesses = 3
    use_sockets = 1
    virtualenv = {{ remote_virtualenv_dir }}
    uid = django
    gid = di

    stderr_stream.class = FileStream
    stdout_stream.filename = {{ remote_shared_path }}/log/circus_error.log
    stdout_stream.time_format = %Y-%m-%d %H:%M:%S
    stdout_stream.max_bytes = 209715200
    stdout_stream.backup_count = 5

    stdout_stream.class = FileStream
    stdout_stream.filename = {{ remote_shared_path }}/log/circus.log
    stdout_stream.time_format = %Y-%m-%d %H:%M:%S
    stdout_stream.max_bytes = 209715200
    stdout_stream.backup_count = 5

    [socket:{{ application_name }}]
    host = {{ socket_host }}
    port = {{ socket_port }}
    """

    fabtools.require.files.directory(
        path=os.path.join(env.remote_home, '.circus.d'),
        use_sudo=True,
        owner=env.remote_owner,
        group=env.remote_group,
        mode='750')

    fabtools.require.files.template_file(
        path=os.path.join(env.remote_home, '.circus.d',
                          'cmscts.ini'),
        template_contents=CIRCUS_INI_FILE,
        context=env,
        use_sudo=True,
        owner=env.remote_owner,
        group=env.remote_group,
        mode='644')


def upstart():
    """
    """

    UPSTART_CONF = """\
    start on filesystem and net-device-up IFACE=lo

    stop on started shutdown

    respawn
    exec /usr/local/bin/circusd {{ remote_home }}/.circus.ini
    """

    # init files to declare circus as an upstart daemon
    fabtools.files.upload_template(UPSTART_CONF,
                                   '/etc/init/circus.conf',
                                   context=env,
                                   use_sudo=True,
                                   user='root',
                                   chown=True,
                                   mode='644',
                                   use_jinja=True)


def app_reload():
    """Start/Restart app using circus"""
    if not 'running' in sudo('status circus'):
        sudo('start circus')
    else:
        with settings(sudo_user=env.remote_owner):
            sudo('circusctl restart %s' % env.application_name)
