
from fabric.api import env
from fabric.api import exists
from fabtools import require

from pydiploy import require as dip_require
from pydiploy import database


def pre_install(tmp_directory, media_root, local_settings_context):
    dip_require.django.base_conf(media_root)
    require.files.directory(env.remote_workdir)
    require.files.directory(env.remote_logdir)
    if local_settings_context is not None:
        dip_require.django.settings(tmp_directory, local_settings_context)


def install(tmp_directory):
    dip_require.python.install(tmp_directory)
    database.install()


def post_install(tmp_directory):
    dip_require.django.manager()

    static_temp = '%s/src/%s/static' % (tmp_directory, env.project_name)
    if exists(static_temp):
        dip_require.django.staticfiles(static_temp)

    local_temp = '%s/src/%s/locale' % (tmp_directory, env.project_name)
    if exists(local_temp):
        dip_require.django.locale(local_temp)

    require.files.directory(env.django_media_root, use_sudo=True,
            owner='django', group='di')

def deploy(tmp_directory, local_settings_context=None,
        media_root='/var/www/data'):
    pre_install(tmp_directory, media_root, local_settings_context)
    install(tmp_directory)
    post_install(tmp_directory)
