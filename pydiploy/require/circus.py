# -*- coding: utf-8 -*-

"""

Methods to install circus package



.. seealso::

    `circus documentation <http://circus.readthedocs.org>`_
      Circus official documentation.

"""

import os
from pydiploy.decorators import do_verbose
import fabric
import fabtools
from fabric.api import env


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
                                    use_sudo=True)

    if 'no_circus_web' not in env or not env.no_circus_web:
        fabtools.require.python.install('circus-web', use_sudo=True)
        fabtools.require.python.install('gevent', use_sudo=True)

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

    # TODO: implement as systemd service !!!
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

    if not 'running' in fabric.api.sudo('status circus'):
        fabric.api.sudo('start circus')
    else:
        with fabric.api.settings(sudo_user=env.remote_owner):
            fabric.api.sudo('circusctl reloadconfig')
            fabric.api.sudo('circusctl restart %s' % env.application_name)
