# -*- coding: utf-8 -*-

"""

Apache webserver relatives methods
==================================

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

    fabtools.require.files.directory(
        env.remote_static_root, use_sudo=True, owner='root', group='root', mode='755'
    )


@do_verbose
def apache_pkg(update=False):
    """ Installs apache package on remote server """

    fabtools.require.deb.packages(['apache2'], update=update)


@do_verbose
def apache_start():
    """ Starts apache """

    try:
        if env.apache_start_confirmation:
            fabric.api.execute(apache_confirm_start)
    except:
        fabtools.service.start('apache2')


@do_verbose
def apache_reload():
    """ Starts/reloads apache """

    if not apache_started():
        fabric.api.execute(apache_start)
    else:
        fabtools.service.reload('apache2')


@do_verbose
def apache_restart():
    """ Starts/Restarts apache """

    if not apache_started():
        fabric.api.execute(apache_start)
    else:
        fabtools.service.restart('apache2')


@do_verbose
def apache_started():
    """ Returns true/false depending on apache service is started """

    return fabtools.service.is_running('apache2')


@do_verbose
def apache_confirm_start():
    """ Confirms launch of apache """

    current_role = pydiploy.prepare._get_current_role()
    if fabric.contrib.console.confirm(
        "\napache on %s (role %s) seems not to be started ! \
                    \n\nDo you want to try to start it?"
        % (fabric.colors.red(env.host), fabric.colors.red(current_role)),
        default=False,
    ):
        fabtools.service.start('apache2')


@do_verbose
def web_configuration():
    """ Setups webserver's configuration """

    fabric.api.execute(up_site_config)
    fabric.api.execute(down_site_config)
    fabric.api.execute(apache_disable_site, '000-default')


@do_verbose
def up_site_config():
    """ Uploads site config for apache """

    apache_root = '/etc/apache2'
    apache_available = os.path.join(apache_root, 'sites-available')
    apache_enabled = os.path.join(apache_root, 'sites-enabled')
    app_conf = os.path.join(apache_available, '%s.conf' % env.server_name)

    fabtools.files.upload_template(
        'apache_host.conf.tpl',
        app_conf,
        context=env,
        template_dir=os.path.join(env.lib_path, 'templates'),
        use_jinja=True,
        use_sudo=True,
        user='root',
        chown=True,
        mode='644',
    )

    fabric.api.execute(apache_enable_site, env.server_name)


@do_verbose
def down_site_config():
    """ Uploads site_down config for apache """

    apache_root = '/etc/apache2'
    apache_available = os.path.join(apache_root, 'sites-available')
    app_conf = os.path.join(apache_available, '%s_down.conf' % env.server_name)

    fabtools.files.upload_template(
        'apache_host_down.conf.tpl',
        app_conf,
        context=env,
        template_dir=os.path.join(env.lib_path, 'templates'),
        use_jinja=True,
        use_sudo=True,
        user='root',
        chown=True,
        mode='644',
    )

    # fabric.api.execute(upload_maintenance_page)


@do_verbose
def set_website_up():
    """ Sets website up """

    # apache_root = '/etc/apache2'
    # apache_available = os.path.join(apache_root, 'sites-available')
    # apache_enabled = os.path.join(apache_root, 'sites-enabled')
    # app_conf = os.path.join(apache_available, '%s.conf' % env.server_name)

    # if not fabtools.files.is_file(app_conf):
    #     fabric.api.execute(up_site_config)

    # if fabtools.files.is_link('%s/%s_down.conf' % (apache_enabled,
    #                                                env.server_name)):
    #     with fabric.api.cd(apache_enabled):
    #         fabric.api.sudo('rm -f %s_down.conf' % env.server_name)

    # if not fabtools.files.is_link('%s/%s.conf' % (apache_enabled,
    #                                               env.server_name)):
    #     with fabric.api.cd(apache_enabled):
    #         fabric.api.sudo('ln -s %s .' % app_conf)

    fabric.api.execute(apache_disable_site, '%s_down' % env.server_name)
    fabric.api.execute(apache_enable_site, '%s' % env.server_name)


@do_verbose
def set_website_down():
    """ Sets website down """

    # apache_root = '/etc/apache2'
    # apache_available = os.path.join(apache_root, 'sites-available')
    # apache_enabled = os.path.join(apache_root, 'sites-enabled')
    # app_down_conf = os.path.join(
    #     apache_available, '%s_down.conf' % env.server_name)

    # if not fabtools.files.is_file(app_down_conf):
    #     fabric.api.execute(down_site_config)

    # if fabtools.files.is_link('%s/%s.conf' % (apache_enabled,
    #                                           env.server_name)):
    #     with fabric.api.cd(apache_enabled):
    #         fabric.api.sudo('rm -f %s.conf' % env.server_name)

    # if not fabtools.files.is_link('%s/%s_down.conf' % (apache_enabled,
    #                                                    env.server_name)):
    #     with fabric.api.cd(apache_enabled):
    #         fabric.api.sudo('ln -s %s .' % app_down_conf)

    apache_disable_site('%s' % env.server_name)
    apache_enable_site('%s_down' % env.server_name)
    # fabric.api.execute(apache_reload)


@do_verbose
def upload_maintenance_page():
    """ Uploads and forges maintenance.html according to template """

    maintenance_file = os.path.join(
        env.remote_static_root, env.application_name, 'maintenance.html'
    )
    vars_required = ['maintenance_text', 'maintenance_title']

    for v in vars_required:
        if v in env:
            env[v] = env[v].decode('utf-8')

    fabtools.files.upload_template(
        'maintenance.html.tpl',
        maintenance_file,
        context=env,
        template_dir=os.path.join(env.lib_path, 'templates'),
        use_jinja=True,
        use_sudo=True,
        user='root',
        chown=True,
        mode='644',
    )


@do_verbose
def enable_apache_modules():
    """ Enables one or many apache modules needed """

    if env.has_key('extra_apache_enabled_modules'):
        for apache_module in env.extra_apache_modules:
            fabtools.require.apache.module_enabled(apache_module)


@do_verbose
def disable_apache_modules():
    """ Enables one or many apache modules needed """

    if env.has_key('extra_apache_disabled_modules'):
        for apache_module in env.extra_apache_modules:
            fabtools.require.apache.module_disabled(apache_module)


@do_verbose
def apache_enable_site(site=None, restart=False):
    """ Enables a site (eg : a2enssite site) """

    if site:
        fabtools.require.apache.site_enabled(
            site
        ) if restart else fabtools.require.apache.site_enabled(site)


@do_verbose
def apache_disable_site(site=None, restart=False):
    """ Disables a site (eg : a2dissite site) """

    if site:
        fabtools.require.apache.site_disabled(site)
