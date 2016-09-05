[Unit]
Description=Circus process manager
After=syslog.target network.target nss-lookup.target

[Service]
Type=simple
ExecReload=/usr/local/bin/circusctl reload
ExecStart=/usr/local/bin/circusd {{ remote_home }}/.circus.ini
Restart=always
RestartSec=5

[Install]
WantedBy=default.target
