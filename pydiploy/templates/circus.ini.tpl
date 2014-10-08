[circus]
httpd = 1
httpd_host = {{ host }}
httpd_port = 8080
stream_backend = gevent
statsd = 1
pidfile = {{ remote_home }}/.circus.pid
include_dir = {{ remote_home }}/.circus.d
