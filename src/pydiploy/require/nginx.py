# -*- coding: utf-8 -*-

"""
"""
import os
from fabric.api import env, require, cd, sudo
from fabric.contrib.project import rsync_project
import fabtools


def gunicorn_site_proxy(user, redirect_port_80=False):
    require('appdir', 'http_port', 'virtualhost', 'gunicorn_port')
    env.proxy_url = 'http://127.0.0.1:%s' % env.gunicorn_port

    if redirect_port_80:
        template_contents = DJANGO_HTTPS + DJANGO_NGINX
    else:
        template_contents = DJANGO_HTTP + DJANGO_NGINX

    fabtools.require.nginx.site(env.virtualhost,
                                template_contents=template_contents, **env)


DJANGO_HTTPS = """\
server {
    listen 80;
    server_name %(virtualhost)s;

    return 301 https://$hosts$request_uri;
}

server {
    listen %(http_port)s;
    server_name %(virtualhost)s;

    ssl                 on;
    ssl_certificate     $(ssl_cert_file)$;
    ssl_certificate_key $(ssl_cert_key)$;

"""

DJANGO_HTTP = """\
server {
    listen %(http_port)s;
    server_name %(virtualhost)s;

"""

DJANGO_NGINX = """\
    access_log  /var/log/nginx/%(virtualhost)s.access.log;
    root   %(appdir)s;

    gzip_vary on;

    try_files $uri @proxied;

    location /static {
            if ($query_string) {
                    expires max;
            }
    }

    location /media {
            root /var/www/data/%(virtualhost)s;
            if ($query_string) {
                    expires max;
            }
    }


    location / {
            proxy_pass_header Server;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header Host $http_host;
            proxy_redirect off;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Scheme $scheme;
            proxy_connect_timeout 10;
            proxy_read_timeout 10;
            proxy_pass %(proxy_url)s;
            client_max_body_size 4M;
    }

    #error_page  404  /404.html;

    # redirect server error pages to the static page /50x.html
    #
    error_page   500 502 503 504  /50x.html;
    location = /50x.html {
            root   /var/www/nginx-default;
    }

}
"""


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
    nginx_root = '/etc/nginx'
    nginx_available = nginx_root + '/sites-available'
    nginx_enabled = nginx_root + '/sites-enabled'
    cmscts_conf = '%s/%s.conf' % (nginx_available, env.server_name)
    fabtools.files.upload_template('fabfile/.cmscts.conf',
                                   cmscts_conf,
                                   context=env,
                                   use_jinja=True,
                                   use_sudo=True,
                                   user='root',
                                   chown=True,
                                   mode='644')

    if not fabtools.files.is_link('%s/%s.conf' % (nginx_enabled,
                                                  env.server_name)):
        with cd(nginx_enabled):
            sudo('ln -s %s .' % cmscts_conf)
            sudo('rm default')
