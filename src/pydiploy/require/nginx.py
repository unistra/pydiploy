"""
"""

from fabric.api import env
from fabtools import require


def django_proxied_site():
    require.nginx.site(env.virtualhost, template_contents=DJANGO_NGINX,
            docroot=env.remote_workdir, port=env.nginx_port,
            proxy_url="http://127.0.0.1:%s" % env.gunicorn_port)


DJANGO_NGINX = """\
server {
        listen %(port)s;
        server_name %(server_name)s;

        access_log  /var/log/nginx/%(server_name)s.access.log;
        root   %(docroot)s;

        gzip_vary on;

        try_files $uri @proxied;

        location /static {
                if ($query_string) {
                        expires max;
                }
        }
        
        location /media {
                root /var/www/data/%(server_name)s;
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
