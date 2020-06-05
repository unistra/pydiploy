<VirtualHost *:%(port)s>
    ServerName {{ server_name }}

    DocumentRoot {{ remote_home }}/{{ server_name }}/current

    <Directory {{ remote_home }}/{{ server_name }}/current>
        Options Indexes FollowSymLinks MultiViews

        AllowOverride All

        Order allow,deny
        allow from all
    </Directory>
</VirtualHost>
