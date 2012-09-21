"""
"""


from fabric.api import env


def base_conf(remote_basedir, project_name):
    env.virtualenv_dir = '%s/.virtualenvs/%s' % (remote_basedir, project_name)
