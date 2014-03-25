# -*- coding: utf-8 -*-

"""
"""
import os
from fabric.api import env, cd, sudo
from fabric.contrib.project import rsync_project
import fabtools


def root_web():
    """
    """
    fabtools.require.files.directory(env.remote_static_root, use_sudo=True,
                                     owner='root', group='root', mode='755')


def nginx_pkg(update=False):
    """
    """
    fabtools.require.deb.packages(['nginx'], update=update)


def nginx_reload():
    """Start/Restart nginx"""
    if not fabtools.service.is_running('nginx'):
        fabtools.service.start('nginx')
    else:
        fabtools.service.reload('nginx')


def web_static_files():
    rsync_project(os.path.join(env.remote_static_root, env.application_name),
                  os.path.join(env.local_tmp_dir, 'assets/'), delete=True,
                  extra_opts='--rsync-path="sudo rsync"',
                  ssh_opts='-t')


def web_configuration():
    """Setup webserver's configuration"""

    APP_NGINX_CONF = """\
    upstream {{ short_server_name }}  {
    {% for backend in backends %}
        server {{ backend }}:{{ socket_port }};
    {% endfor %}
    }

    {% if server_ssl_on %}
    server {
        listen {% if server_ip %}{{ server_ip }}:{% endif %}80;
        server_name {{ server_name }} {{ short_server_name }};

        rewrite             ^ https://$server_name$request_uri? permanent;
    }
    {% endif %}

    server {
        listen {% if server_ip %}{{ server_ip }}:{% endif %}{% if server_ssl_on %}443{% else %}80{% endif %};
        server_name {{ server_name }} {{ short_server_name }};

    {% if server_ssl_on %}
        ssl                  on;
        ssl_certificate      /etc/ssl/certs/wildcard.u-strasbg.fr.pem;
        ssl_certificate_key  /etc/ssl/private/wildcard.u-strasbg.fr.key;
    {% endif %}

        location = /favicon.ico {
          log_not_found off;
        }

        location /site_media/ {
                    alias {{ remote_current_path }}/assets/;
                    autoindex on;
                    allow all;

        }


        location / {
            # Correspond au nom defini dans 'upstream'
            proxy_pass      http://{{ short_server_name }}$request_uri;
            proxy_redirect  off;

        {% if server_ip %}
            proxy_bind      {{ server_ip }};
        {% endif %}
            resolver        130.79.200.200;

            proxy_set_header   Host             $host;
            proxy_set_header   X-Real-IP        $remote_addr;
            proxy_set_header   X-Forwarded-For  $proxy_add_x_forwarded_for;
            proxy_set_header   X-Forwarded-Protocol ssl;
            proxy_set_header   X-Forwarded-Ssl on;
        }
        {% if server_ssl_on %}
            access_log  /var/log/nginx/{{ short_server_name }}_ssl.access.log;
            error_log  /var/log/nginx/{{ short_server_name }}_ssl.error.log warn;
        {% else %}
            access_log  /var/log/nginx/{{ short_server_name }}.log;
            error_log  /var/log/nginx/{{ short_server_name }}.log warn;
        {% endif %}
    }
    """

    nginx_root = '/etc/nginx'
    nginx_available = nginx_root + '/sites-available'
    nginx_enabled = nginx_root + '/sites-enabled'
    app_conf = '%s/%s.conf' % (nginx_available, env.server_name)
    fabtools.files.upload_template('fabfile/.cmscts.conf',
                                   app_conf,
                                   context=env,
                                   use_jinja=True,
                                   use_sudo=True,
                                   user='root',
                                   chown=True,
                                   mode='644')

    if not fabtools.files.is_link('%s/%s.conf' % (nginx_enabled,
                                                  env.server_name)):
        with cd(nginx_enabled):
            sudo('ln -s %s .' % app_conf)
            sudo('rm default')
