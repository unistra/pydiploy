"""
"""

from fabric.api import env
from fabtools import require


def gunicorn_site_proxy(redirect_port_80=False):
    require('appdir', 'http_port', 'virtualhost', 'gunicorn_port')
    env.proxy_url = 'http://127.0.0.1:%s' % env.gunicorn_port
    
    if redirect_port_80:
        template_contents = DJANGO_HTTPS + DJANGO_NGINX
    else
        template_contents = DJANGO_HTTP + DJANGO_NGINX

    fabtools.require.nginx.site(env.virtualhost,
        template_contents=template_contents, context=env)


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
