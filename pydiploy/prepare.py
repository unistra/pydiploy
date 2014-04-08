# -*- coding: utf-8 -*-

""" Ce module contient toutes les tâches nécessaires à la préparation d'une machine virtuelle en vue du déploiement
d'une application Python. Les fonctions acessibles via les tâches `Fabric <http://docs.fabfile.org/en/latest/>`_ sont:

* install_tools : installation d'outils standards
* create_python_env : création de l'environnement Python
* update_python_env : mise à jour de l'environnement Python
* oracle_client : préparation de la machine à l'installation du client Oracle pour Python
* sap_client : préparation de la machine à l'installation du client SAP pour Python
"""

import os

from fabric.api import env
import fabric
import fabtools


@fabric.api.task
def tag(version):
    """ """
    env.tag = version


def build_env():
    # check if tag is specified if not fabric.api.prompt user
    if "tag" not in env:
        env.tag = fabric.api.prompt('Please specify target tag used: ')

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
