"""
Gunicorn
========

.. gunicorn: http://gunicorn.org

"""

import os

from fabric.api import env
from fabric.api import require
import fabtools


def server():
    """
    """
    with fabtools.python.virtualenv(env.virtualenvdir):
        fabtools.require.python.package('gunicorn', upgrade=True)


def launcher(user, group, with_upstart=False, **kwargs):
    """
    """
    require('appdir', 'project_name', 'owner_user', 'owner_group',
            'virtualenvdir', 'gunicorn_workers', 'gunicorn_loglevel',
            'gunicorn_port')

    server()
    fabtools.require.files.directory(os.path.join(env.appdir, 'bin'),
                                     use_sudo=True, owner=user, group=group, mode='755')
    launcher_filename = os.path.join(env.appdir, 'bin', env.project_name)
    fabtools.require.files.template_file(path=launcher_filename,
                                         template_contents=GUNICORN_APP_LAUNCHER, context=env,
                                         mode='700', owner=user, use_sudo=True)

    if with_upstart:
        instance_name = '%(project_name)s %(env)s' % env
        upstart(launcher_filename, instance_name)


GUNICORN_APP_LAUNCHER = """\
#!/bin/bash
set -e
LOGFILE=%(appdir)s/log/gunicorn.log
NUM_WORKERS=%(gunicorn_workers)s
# user/group to run as
USER=%(owner_user)s
GROUP=%(owner_group)s
HOST=127.0.0.1
PORT=%(gunicorn_port)s
LOG_LEVEL=%(gunicorn_loglevel)s
cd %(appdir)s
source %(virtualenvdir)s/bin/activate
exec %(virtualenvdir)s/bin/gunicorn %(project_name)s.wsgi:application \
    -w $NUM_WORKERS --user=$USER --group=$GROUP --log-level=$LOG_LEVEL \
    -b $HOST:$PORT -p %(project_name)s.pid -t 60 --log-file=$LOGFILE \
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
