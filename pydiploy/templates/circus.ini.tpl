[circus]
{% if no_circus_web %}
# set httpd to 1 if you want to activate circus-web and uncomment the following lines
httpd = 0
#httpd_host = {{ host }}
#httpd_port = 8080
{% if circus_backend %}
stream_backend = {{ circus_backend }} 
{% else %}
#stream_backend = gevent
{% endif %}
{% else %}
httpd = 1
httpd_host = {{ host }}
httpd_port = 8080
{% if circus_backend %}
stream_backend = {{ circus_backend }}
{% else %}
stream_backend = gevent
{% endif %}
{% endif %}
statsd = 1
pidfile = {{ remote_home }}/.circus.pid
include_dir = {{ remote_home }}/.circus.d
