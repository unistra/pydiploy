"""
"""


from fabric.api import cd
from fabric.api import env
from fabric.api import get
from fabric.api import require as req
from fabric.api import run

import fabtools
from fabtools import require


def base_conf(media_root):
    """
    """
    env.remote_workdir = '%(remote_basedir)s/%(virtualhost)s' % env
    env.remote_logdir = '%(remote_workdir)s/log' % env
    env.django_settings_module = '%(project_name)s.settings' % env
    env.django_media_root = '%s/%s' % (media_root, env.virtualhost)


def manager(temp_dir):
    req('project_name, remote_workdir')
    with cd(env.remote_workdir):
        run('cp %s/src/%s/manage.py .' % (temp_dir, env.project_name))


def staticfiles(temp_dir):
    req('project_name, remote_workdir')
    with cd(env.remote_workdir):
        run('cp -R %s/src/%/static _static' % (temp_dir, env.project_name))
        run('python manage.py collectstatic -c -l --noinput')


def locales(temp_dir):
    req('project_name, remote_workdir')
    with cd(env.remote_workdir):
        run('cp -R %s/src/%s/locale .' % temp_dir, env.project_name)
        run('python manage.py compilemessages')


def settings(temp_dir, context):
    req('project_name, remote_workdir')
    with cd(temp_dir):
        get('conf/local_settings.py.template', '/tmp/local_settings.py')
    require.files.template_file(
            path='%s/src/%s/local_settings.py' % (temp_dir, env.project_name),
            template_source='/tmp/local_settings.py', context=context)


def db_engines():
    """
    """
    with fabtools.python.virtualenv(env.virtualenv_dir):
        from django.conf.settings import DATABASES
        return [database['ENGINE'].split('.')[-1] for database 
                in DATABASES.itervalues()]
