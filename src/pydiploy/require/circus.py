# -*- coding: utf-8 -*-

import os
from fabric.api import env, sudo, settings
import fabtools


def circus(update=False):
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
    fabtools.files.upload_template('fabfile/.circus.ini',
                                   os.path.join(
                                       env.remote_home, '.circus.ini'),
                                   context=env,
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
    # init files to declare circus as an upstart daemon
    fabtools.files.upload_template('fabfile/.circus.init.conf',
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


def app_circus_conf():
    fabtools.files.upload_template('fabfile/.cmscts.ini',
                                   os.path.join(env.remote_home, '.circus.d',
                                                'cmscts.ini'),
                                   context=env,
                                   use_sudo=True,
                                   user=env.remote_owner,
                                   chown=True,
                                   mode='644',
                                   use_jinja=True)
