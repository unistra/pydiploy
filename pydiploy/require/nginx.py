# -*- coding: utf-8 -*-

"""
"""
import os
from fabric.api import env
import fabric
import fabtools


def root_web():
    """ Creates web root for webserver """

    fabtools.require.files.directory(env.remote_static_root, use_sudo=True,
                                     owner='root', group='root', mode='755')


def nginx_pkg(update=False):
    """ Installs nginx package on remote server """

    fabtools.require.deb.packages(['nginx'], update=update)


def nginx_reload():
    """ Starts/Reloads nginx """

    if not fabtools.service.is_running('nginx'):
        fabtools.service.start('nginx')
    else:
        fabtools.service.reload('nginx')


def nginx_restart():
    """ Starts/Restarts nginx """

    if not fabtools.service.is_running('nginx'):
        fabtools.service.start('nginx')
    else:
        fabtools.service.restart('nginx')


def web_static_files():
    """ Syncs statics files """

    fabric.contrib.project.rsync_project(
        os.path.join(env.remote_static_root, env.application_name),
        os.path.join(env.local_tmp_dir, 'assets/'), delete=True,
        extra_opts='--rsync-path="sudo rsync"',
        ssh_opts='-t')


def web_configuration():
    """ Setups webserver's configuration """

    nginx_root = '/etc/nginx'
    nginx_available = os.path.join(nginx_root, 'sites-available')
    nginx_enabled = os.path.join(nginx_root, 'sites-enabled')
    app_conf = os.path.join(nginx_available, '%s.conf' % env.server_name)

    fabtools.files.upload_template('nginx.conf.tpl',
                                   app_conf,
                                   context=env,
                                   template_dir=os.path.join(
                                       env.lib_path, 'templates'),
                                   use_jinja=True,
                                   use_sudo=True,
                                   user='root',
                                   chown=True,
                                   mode='644')

    if not fabtools.files.is_link('%s/%s.conf' % (nginx_enabled,
                                                  env.server_name)):
        with fabric.api.cd(nginx_enabled):
            fabric.api.sudo('ln -s %s .' % app_conf)
            fabric.api.sudo('rm -f default')
