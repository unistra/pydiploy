start on filesystem and net-device-up IFACE=lo

stop on started shutdown

respawn
exec /usr/local/bin/circusd {{ remote_home }}/.circus.ini
