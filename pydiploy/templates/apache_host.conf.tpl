{% if apache_custom_vhost %}
{{ apache_custom_vhost }}
{% else %}
<VirtualHost *:{{ apache_port }}>
    ServerName {{ server_name }}

    DocumentRoot {{ remote_home }}/{{ server_name }}/current

    <Directory {{ remote_home }}/{{ server_name }}/current>
        Options Indexes FollowSymLinks MultiViews

        AllowOverride All

        Order allow,deny
        allow from all
    </Directory>
</VirtualHost>
{% endif %}