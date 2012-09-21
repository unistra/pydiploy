"""
"""


from fabric.api import env
from fabric.api import require
from fabric.api import run


def base_conf(remote_basedir, project_name, virtualhost, media_root):
    """
    """
    env.remote_basedir = remote_basedir
    env.remote_workdir = '%(remote_basedir)s/%(virtualhost)s' % locals()
    env.remote_logdir = '%(remote_basedir)s' % locals()
    env.django_settings_module = '%(project_name)s.settings' % locals()
    env.django_media_root = '%(media_root)s/%(virtualhost)s' % locals()


def copy_manager(temp_dir):
    require('project_name')
    run('cp %s/src/%s/manager.py %s' % (temp_dir, env.project_name,
        env.remote_workdir))
