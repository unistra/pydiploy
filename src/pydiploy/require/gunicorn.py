"""
Gunicorn
========

.. gunicorn: http://gunicorn.org

"""

from fabric.api import env
import fabtools


def server():
    """
    """
    with fabtools.python.virtualenv(env.virtualenv_dir):
        fabtools.require.python.package('gunicorn', upgrade=True)


def launcher(with_upstart=False):
    """
    """
    server()
    
    fabtools.require.files.directory('%(remote_workdir)s/bin' % env)
    launcher_filename = '%(remote_workdir)s/bin/%(project_name)s' % env
    context = {
        'appdir': env.remote_workdir,
        'workers': env.gunicorn_workers,
        'user': env.user,
        'group': env.group,
        'port': env.gunicorn_port,
        'log_level': env.gunicorn_loglevel,
        'virtualenv': env.virtualenv_dir,
        'settings_package': env.project_name

    }
    fabtools.require.files.template_file(path=launcher_filename,
            template_contents=GUNICORN_APP_LAUNCHER, context=context,
            mode='700')

    if with_upstart:
        instance_name = '%(project_name)s %(env)s' % env
        upstart(launcher_filename, instance_name)


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
LOG_LEVEL=%(log_level)s
cd %(appdir)s
source %(virtualenv)s/bin/activate
exec %(virtualenv)s/bin/gunicorn %(settings_package)s.wsgi:application \
    -w $NUM_WORKERS --user=$USER --group=$GROUP --log-level=$LOG_LEVEL \
    -b $HOST:$PORT -p %(settings_package)s.pid -t 60 --log-file=$LOGFILE \
    2>>$LOGFILE
"""


def upstart(gunicorn_launcher, instance_name):
    """
    """
    upstart_filename = '/etc/init/%(project_name)s.conf' % env
    context = {
        'instance_name': instance_name,
        'gunicorn_launcher': gunicorn_launcher
    }

    fabtools.require.files.template_file(path=upstart_filename,
            template_contents=UPSTART_CONF, context=context, use_sudo=True)


UPSTART_CONF = """\
description "%(instance_name)s instance"
start on runlevel [2345]
stop on runlevel [06]
respawn
respawn limit 10 5
exec %(gunicorn_launcher)s
"""
