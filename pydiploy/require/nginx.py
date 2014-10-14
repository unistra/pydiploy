# -*- coding: utf-8 -*-

"""
"""
import os

import fabric
import fabtools
from fabric.api import env


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
        extra_opts='--rsync-path="sudo rsync" --exclude="maintenance.html"',
        ssh_opts='-t')


def web_configuration():
    """ Setups webserver's configuration """

    nginx_root = '/etc/nginx'
    nginx_available = os.path.join(nginx_root, 'sites-available')
    nginx_enabled = os.path.join(nginx_root, 'sites-enabled')
    app_conf = os.path.join(nginx_available, '%s.conf' % env.server_name)

    fabric.api.execute(up_site_config)
    fabric.api.execute(down_site_config)

    if fabtools.files.is_link('%s/default' % nginx_enabled):
        with fabric.api.cd(nginx_enabled):
            fabric.api.sudo('rm -f default')


def up_site_config():
    """ upload site config for nginx """
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


def down_site_config():
    """ upload site_down config for nginx """

    nginx_root = '/etc/nginx'
    nginx_available = os.path.join(nginx_root, 'sites-available')
    app_conf = os.path.join(nginx_available, '%s_down.conf' % env.server_name)
    maintenance_file = os.path.join(env.remote_static_root, env.application_name, 'maintenance.html')
    fabtools.files.upload_template('nginx_down.conf.tpl',
                                   app_conf,
                                   context=env,
                                   template_dir=os.path.join(
                                       env.lib_path, 'templates'),
                                   use_jinja=True,
                                   use_sudo=True,
                                   user='root',
                                   chown=True,
                                   mode='644')

    fabtools.files.upload_template('maitenance.html.tpl',
                                   maintenance_file,
                                   context=env,
                                   template_dir=os.path.join(
                                       env.lib_path, 'templates'),
                                   use_jinja=True,
                                   use_sudo=True,
                                   user='root',
                                   chown=True,
                                   mode='644')


def set_website_up():
    """ set websiste up """

    nginx_root = '/etc/nginx'
    nginx_available = os.path.join(nginx_root, 'sites-available')
    nginx_enabled = os.path.join(nginx_root, 'sites-enabled')
    app_conf = os.path.join(nginx_available, '%s.conf' % env.server_name)

    if not fabtools.files.is_file(app_conf):
        fabric.api.execute(up_site_config)

    if fabtools.files.is_link('%s/%s_down.conf' % (nginx_enabled,
                                                   env.server_name)):
        with fabric.api.cd(nginx_enabled):
            fabric.api.sudo('rm -f %s_down.conf' % env.server_name)

    if not fabtools.files.is_link('%s/%s.conf' % (nginx_enabled,
                                                  env.server_name)):
        with fabric.api.cd(nginx_enabled):
            fabric.api.sudo('ln -s %s .' % app_conf)

    fabric.api.execute(nginx_restart)


def set_website_down():
    """ set websiste down """

    nginx_root = '/etc/nginx'
    nginx_available = os.path.join(nginx_root, 'sites-available')
    nginx_enabled = os.path.join(nginx_root, 'sites-enabled')
    app_down_conf = os.path.join(
        nginx_available, '%s_down.conf' % env.server_name)

    if not fabtools.files.is_file(app_down_conf):
        fabric.api.execute(down_site_config)

    if fabtools.files.is_link('%s/%s.conf' % (nginx_enabled,
                                              env.server_name)):
        with fabric.api.cd(nginx_enabled):
            fabric.api.sudo('rm -f %s.conf' % env.server_name)

    if not fabtools.files.is_link('%s/%s_down.conf' % (nginx_enabled,
                                                       env.server_name)):
        with fabric.api.cd(nginx_enabled):
            fabric.api.sudo('ln -s %s .' % app_down_conf)

    fabric.api.execute(nginx_restart)
