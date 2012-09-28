"""
"""


from fabric.api import cd
from fabric.api import env
from fabric.api import get
from fabric.api import require as req
from fabric.api import run

import fabtools
from fabtools import require


def manager(temp_dir):
    req('project_name', 'remote_workdir')
    with cd(env.remote_workdir):
        run('cp %s/src/%s/manage.py .' % (temp_dir, env.project_name))


def staticfiles(temp_dir):
    req('project_name', 'remote_workdir')
    run('cp -R %s/src/%s/static %s/_static' % (temp_dir, env.project_name,
        env.remote_workdir))
    require.files.directory('%(remote_workdir)s/static' % env)
    with fabtools.python.virtualenv(env.virtualenv_dir):
        with cd(env.remote_workdir):
            run('python manage.py collectstatic -c -l --noinput')


def locales(temp_dir):
    req('project_name', 'remote_workdir')
    run('cp -R %s/src/%s/locale %s' % (temp_dir, env.project_name,
        env.remote_workdir))
    with fabtools.python.virtualenv(env.virtualenv_dir):
        with cd(env.remote_workdir):
            run('python manage.py compilemessages')


def settings(temp_dir):
    req('project_name', 'remote_workdir')
    with cd(temp_dir):
        get('conf/local_settings.py.template', '/tmp/local_settings.py')
    require.files.template_file(
            path='%s/src/%s/%s/local_settings.py' % (temp_dir,
                env.project_name, env.project_name),
            template_source='/tmp/local_settings.py', context=env)


def db_engines():
    """
    """
    with fabtools.python.virtualenv(env.virtualenv_dir):
        from django.conf import settings
        return [database['ENGINE'].split('.')[-1] for database 
                in settings.DATABASES.itervalues()]
