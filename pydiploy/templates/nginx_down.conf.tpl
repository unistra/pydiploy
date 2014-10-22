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

    root {{ remote_static_root }}/{{ application_name }}/;
    error_page 503 /maintenance.html;

    location /maintenance.html {
        # allow access to this specific page
    }
    location / {
        return 503;
    }
}
