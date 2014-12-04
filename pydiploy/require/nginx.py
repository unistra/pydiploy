# -*- coding: utf-8 -*-

"""
"""
import os

import fabric
import fabtools
import pydiploy
from fabric.api import env
from pydiploy.decorators import do_verbose


@do_verbose
def root_web():
    """ Creates web root for webserver """

    fabtools.require.files.directory(env.remote_static_root, use_sudo=True,
                                     owner='root', group='root', mode='755')


@do_verbose
def nginx_pkg(update=False):
    """ Installs nginx package on remote server """

    fabtools.require.deb.packages(['nginx'], update=update)


@do_verbose
def nginx_start():
    """ Starts nginx """

    try:
        if env.nginx_start_confirmation:
            fabric.api.execute(nginx_confirm_start)
    except:
        fabtools.service.start('nginx')


@do_verbose
def nginx_reload():
    """ Starts/reloads nginx """

    if not nginx_started():
        fabric.api.execute(nginx_start)
    else:
        fabtools.service.reload('nginx')


@do_verbose
def nginx_restart():
    """ Starts/Restarts nginx """

    if not nginx_started():
        fabric.api.execute(nginx_start)
    else:
        fabtools.service.restart('nginx')


@do_verbose
def nginx_started():
    """ Returns true/false depending on nginx service is started """

    return fabtools.service.is_running('nginx')


@do_verbose
def nginx_confirm_start():
    """ Confirms launch of nginx """

    current_role = pydiploy.prepare._get_current_role()
    if fabric.contrib.console.confirm(
        "\nNginx on %s (role %s) seems not to be started ! \
                    \n\nDo you want to try to start it?" %
        (fabric.colors.red(env.host),
         fabric.colors.red(current_role)), default=False):
        fabtools.service.start('nginx')


@do_verbose
def web_static_files():
    """ Syncs statics files """

    fabric.contrib.project.rsync_project(
        os.path.join(env.remote_static_root, env.application_name),
        os.path.join(env.local_tmp_dir, 'assets/'), delete=True,
        extra_opts='--rsync-path="sudo rsync" --exclude="maintenance.html"',
        ssh_opts='-t')


@do_verbose
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


@do_verbose
def up_site_config():
    """ Uploads site config for nginx """
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


@do_verbose
def down_site_config():
    """ Uploads site_down config for nginx """

    nginx_root = '/etc/nginx'
    nginx_available = os.path.join(nginx_root, 'sites-available')
    app_conf = os.path.join(nginx_available, '%s_down.conf' % env.server_name)

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

    fabric.api.execute(upload_maintenance_page)


@do_verbose
def set_website_up():
    """ Sets website up """

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


@do_verbose
def set_website_down():
    """ Sets website down """

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


@do_verbose
def upload_maintenance_page():
    """ Uploads and forges maintenance.html according to template """

    maintenance_file = os.path.join(env.remote_static_root,
                                    env.application_name,
                                    'maintenance.html')
    vars_required = ['maintenance_text', 'maintenance_title']

    for v in vars_required:
        if v in env:
            env[v] = env[v].decode('utf-8')

    fabtools.files.upload_template('maintenance.html.tpl',
                                   maintenance_file,
                                   context=env,
                                   template_dir=os.path.join(
                                       env.lib_path, 'templates'),
                                   use_jinja=True,
                                   use_sudo=True,
                                   user='root',
                                   chown=True,
                                   mode='644')
