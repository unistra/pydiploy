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

from string import Template
from fabric.api import env
import fabric
import fabtools


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

def install_oracle_client():
    """
    installs oracle's client for Python oracle_cx.

    needed env vars in fabfile:

    env.oracle_client_version eg : '11.2.0.2.0'
    env.oracle_download_url : eg 'http://libshost/lib/oracle_repo/''
    env.oracle_remote_dir : name of oracle installation directore eg : 'oracle_client'
    env.oracle_packages : name(s) of zip file(s) for oracle's packages to deploy

    """

    # system libs and goodies installation
    fabtools.require.deb.packages(['libaio-dev','unzip'])

    fabtools.require.files.directory(
            path=os.path.join(env.remote_home, env.oracle_remote_dir),
            use_sudo=True,
            owner=env.remote_owner,
            group=env.remote_group,
            mode='750')

    # get oracle's zip file(s) and unzip
    with fabric.api.cd(env.remote_home):
        for package in env.oracle_packages:
            fabric.api.sudo('wget -c %s%s' % (env.oracle_download_url, package))
            fabric.api.sudo('unzip %s -d %s' % (package, env.oracle_remote_dir))
            fabric.api.sudo('rm %s' % os.path.join(env.remote_home,package))

        oracle_dir = 'instantclient_%s' % '_'.join(env.oracle_client_version.split('.')[:2])
        oracle_root_path = os.path.join(env.oracle_remote_dir, oracle_dir)
        oracle_full_path = os.path.join(env.remote_home, oracle_root_path)

        with fabric.api.cd(oracle_root_path):
                if not fabtools.files.is_link('libclntsh.so',use_sudo=True):
                    fabric.api.sudo('ln -s libclntsh.so.* libclntsh.so')

        # library configuration
        oracle_conf = Template(
            "# ORACLE CLIENT CONFIGURATION"
            "\nexport ORACLE_HOME=$oracle_dir"
            "\nexport LD_LIBRARY_PATH=$$LD_LIBRARY_PATH:$$ORACLE_HOME"
        )

        fabric.api.sudo('pwd')
        fabric.api.sudo('echo \'%s\' >> .bashrc' % oracle_conf.substitute(oracle_dir=oracle_full_path))
        fabric.api.sudo('source .bashrc')
        fabric.api.sudo('echo %s > /etc/ld.so.conf.d/oracle.conf' % oracle_full_path)
        fabric.api.sudo('ldconfig')
