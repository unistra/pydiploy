# -*- coding: utf-8 -*-

"""  This module builds env. vars used for the whole library methods are :

* tag : get the tag used to deploy the app
* build_env : inits all env. vars used by the library

"""

import os
import fabric
import fabtools

from fabric.api import env


@fabric.api.task
def tag(version):
    """
    Defines tag to deploy
    """
    env.tag = version


def build_env():
    """
    Builds env vars
    """

    # checks if tag is specified if not fabric.api.prompt user
    if "tag" not in env:
        env.tag = fabric.api.prompt('Please specify target tag used: ')

    # defines destination path for fetched file(s)
    if "dest_path" not in env:
        env.dest_path = env.local_tmp_dir

    env.remote_project_dir = os.path.join(env.remote_home, env.server_name)
    env.local_tmp_root_app = os.path.join(env.local_tmp_dir,
                                          '%(application_name)s-%(tag)s' % env)
    env.local_tmp_root_app_package = os.path.join(env.local_tmp_root_app,
                                                  env.root_package_name)

    env.remote_current_path = os.path.join(env.remote_project_dir, 'current')
    env.remote_releases_path = os.path.join(env.remote_project_dir, 'releases')
    env.remote_shared_path = os.path.join(env.remote_project_dir, 'shared')
    env.remote_base_package_dir = os.path.join(env.remote_current_path,
                                               env.root_package_name)
    env.remote_settings_dir = os.path.join(
        env.remote_base_package_dir, 'settings')
    env.remote_settings_file = os.path.join(env.remote_settings_dir,
                                            '%s.py' % env.goal)

    env.lib_path = os.path.dirname(__file__)

    if not "releases" in env:
        if fabtools.files.is_dir(env.remote_releases_path):
            env.releases = sorted(fabric.api.run('ls -x %(releases_path)s' %
                                                 {'releases_path': env.remote_releases_path}).split())
            if len(env.releases) >= 1:
                env.current_revision = env.releases[-1]
                env.current_release = "%(releases_path)s/%(current_revision)s" % \
                                      {'releases_path': env.remote_releases_path,
                                       'current_revision': env.current_revision}
            if len(env.releases) > 1:
                env.previous_revision = env.releases[-2]
                env.previous_release = "%(releases_path)s/%(previous_revision)s" % \
                                       {'releases_path': env.remote_releases_path,
                                        'previous_revision': env.previous_revision}
