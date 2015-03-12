[watcher:{{ application_name }}]
cmd = {{ remote_virtualenv_dir }}/bin/chaussette{% if chaussette_backend %} --backend {{ chaussette_backend }}{% endif %} --fd $(circus.sockets.{{ application_name }}) {{ root_package_name }}.wsgi.application
working_dir = {{ remote_current_path }}
copy_env = 1
numprocesses = 3
use_sockets = 1
virtualenv = {{ remote_virtualenv_dir }}
virtualenv_py_ver = {{ remote_python_version }}
uid = {{ remote_owner }}
gid = {{ remote_group }}

stderr_stream.class = FileStream
stderr_stream.filename = {{ remote_shared_path }}/log/circus_error.log
stderr_stream.time_format = %Y-%m-%d %H:%M:%S
stderr_stream.max_bytes = 209715200
stderr_stream.backup_count = 5

stdout_stream.class = FileStream
stdout_stream.filename = {{ remote_shared_path }}/log/circus.log
stdout_stream.time_format = %Y-%m-%d %H:%M:%S
stdout_stream.max_bytes = 209715200
stdout_stream.backup_count = 5

[socket:{{ application_name }}]

{% if socket_host %}
host = {{ socket_host }}
{% else %}
host = {{ host }}
{% endif %}


port = {{ socket_port }}
