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

    root {{ static_folder }};
    error_page 503 /maintenance.html;

    location /maintenance.html {
        # allow access to this specific page
    }
    location / {
        return 503;
    }
}
