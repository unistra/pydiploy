upstream {{ short_server_name }}  {
{% if no_shared_sessions %}
ip_hash;
{% endif %}
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
    ssl_certificate      {{ path_to_cert }};
    ssl_certificate_key  {{ path_to_cert_key }};
{% endif %}

    location = /favicon.ico {
      log_not_found off;
    }

    location {{ static_folder }} {
                alias {{ remote_static_root }}/{{ application_name }}/;
                autoindex on;
                allow all;

    }

{% if media_folder is defined and remote_media_folder is defined %}
    location {{ media_folder }} {
                alias {{ remote_media_folder }};
                autoindex off;
                allow all;

    }
{% endif %}

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
        {% if server_ssl_on %}
        proxy_set_header   X-Forwarded-Protocol ssl;
        proxy_set_header   X-Forwarded-Ssl on;
        {% endif %}
        {% if nginx_location_extra_directives %}
        {% for extra_directive in nginx_location_extra_directives %}
        {{ extra_directive }};
        {% endfor %}
        {% endif %}
    }
    {% if server_ssl_on %}
        access_log  /var/log/nginx/{{ short_server_name }}_ssl.access.log;
        error_log  /var/log/nginx/{{ short_server_name }}_ssl.error.log warn;
    {% else %}
        access_log  /var/log/nginx/{{ short_server_name }}.log;
        error_log  /var/log/nginx/{{ short_server_name }}.log warn;
    {% endif %}
}
