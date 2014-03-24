
from fabric.api import env
from fabric.contrib.files import exists
from fabtools import require

from pydiploy import require as dip_require


def pre_install(tmp_directory, with_settings):
    require.files.directory(env.remote_workdir)
    require.files.directory(env.remote_logdir)
    if with_settings:
        dip_require.django.settings(tmp_directory)


def post_install(tmp_directory):
    dip_require.django.manager(tmp_directory)

    static_temp = '%s/src/%s/static' % (tmp_directory, env.project_name)
    if exists(static_temp):
        dip_require.django.staticfiles(tmp_directory)

    local_temp = '%s/src/%s/locale' % (tmp_directory, env.project_name)
    if exists(local_temp):
        dip_require.django.locale(tmp_directory)

    require.files.directory(env.django_media_root, use_sudo=True,
                            owner=env.user, group=env.group)


def install(tmp_directory, with_settings=False):
    pre_install(tmp_directory, with_settings)
    dip_require.python.install(tmp_directory)
    post_install(tmp_directory)
