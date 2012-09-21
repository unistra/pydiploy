"""
Gunicorn
========

.. gunicorn: http://gunicorn.org

"""

from fabric.api import env
from fabtools import require


def server():
    """
    """
    with require.python.virtualenv(env.virtualenv_dir):
        require.python.package('gunicorn', upgrade=True)


def launcher(port, workers=3, user="django", group="di", log_level="ERROR"):
    """
    """
    server()

    launcher_filename = '%(remote_workdir)s/bin/%(project_name)s' % env
    context = {
        'appdir': env.remote_appdir,
        'workers': workers,
        'user': user,
        'group': group,
        'port': port,
        'log_level': log_level,
        'virtualenv': env.virtualenv_dir,
        'settings_package': env.project_name

    }
    require.files.template_file(path=launcher_filename,
            template_contents=GUNICORN_APP_LAUNCHER, context=context)


GUNICORN_APP_LAUNCHER = """\
#!/bin/bash
set -e
LOGFILE=%(appdir)s/log/gunicorn.log
NUM_WORKERS=%(workers)s
# user/group to run as
USER=%(user)s
GROUP=%(group)s
HOST=127.0.0.1
PORT=%(port)s
LOG_LEVEL=%(loglevel)s
cd %(appdir)s
source %(virtualenv)/bin/activate
exec %(virtualenv)s/bin/gunicorn %(settings_package)s.wsgi:application \
    -w $NUM_WORKERS --user=$USER --group=$GROUP --log-level=$LOG_LEVEL \
    -b $HOST:$PORT -p %(settings_package)s.pid -t 60 --log-file=$LOGFILE \
    2>>$LOGFILE
"""


def upstart(gunicorn_launcher="", instance_name=""):
    """
    """
    if not gunicorn_launcher:
        gunicorn_launcher = '%(remote_workdir)s/bin/%(project_name)s' % env
    if not instance_name:
        instance_name = '%(project_name)s %(env)s' % env

    upstart_filename = '/etc/init/%(project_name)s.conf' % env
    context = {
        'instance_name': instance_name,
        'gunicorn_launcher': gunicorn_launcher
    }

    require.files.template_file(path=upstart_filename,
            template_contents=UPSTART_CONF, context=context, use_sudo=True)


UPSTART_CONF = """\
description "%(instance_name)s instance"
start on runlevel [2345]
stop on runlevel [06]
respawn
respawn limit 10 5
exec %(gunicorn_launcher)s
"""
