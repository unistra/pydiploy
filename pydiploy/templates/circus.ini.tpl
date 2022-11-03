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
# set httpd to 1 if you want to activate circus-web and uncomment the following lines
# circus-web not working with python3 so deactivated for now
httpd = 0
httpd_host = {{ host }}
httpd_port = 8080
{% if circus_backend %}
stream_backend = {{ circus_backend }}
{% else %}
stream_backend = gevent
{% endif %}
{% endif %}
# set statsd to 1 to use circus pub/sub mechanism
statsd = 0
pidfile = {{ remote_home }}/.circus.pid
include_dir = {{ remote_home }}/.circus.d
