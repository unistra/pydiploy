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
from fabric.api import env, cd, require, run, sudo, task, prompt
from fabtools import files as fabtoolsfiles


@task
def oracle_client():
    """ Déploiement des fichiers et packages nécessaires à l'installation du client Oracle pour Python
    Cette taĉhe nécessite un environnement Python installé et à jour sur la machine cible et est nécessaire
    à l'installation du client Python oracle_cx.
    """
    # required environnment variables
    require('oracle', 'local_repository')
    # system libs installation
    sudo('aptitude install libaio-dev')

    # needed client packages and installation of them
    packages = [
        'instantclient-basic-linux-x86-64-{version}.zip', 'instantclient-sdk-linux-x86-{version}.zip',
        'instantclient-sqlplus-linux-x86-64-{version}.zip']
    sudo('mkdir -p {home}'.format(**env.oracle))
    for package in packages:
        package = package.format(**env.oracle)
        run('wget http://{0[root]}/{0[libs]/oracle/{1}'.format(
            env.local_repository, package))
        sudo('unzip -d {0[home]} $HOME/{1}'.format(env.oracle, package))
        run('rm $HOME/{0}'.format(package))
    oracle_dir = '{home}/instantclient_'.format(
        **env.oracle) + '_'.join(env.oracle['version'].split('.')[:2])
    with cd(oracle_dir):
        run('ln -s libclntsh.so.* libclntsh.so')

    # library configuration
    oracle_conf = Template(
        "\n# ORACLE CLIENT CONFIGURATION"
        "export ORACLE_HOME=$oracle_dir"
        "export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$ORACLE_HOME"
    )
    run('echo {0} >> $HOME/.bash_profile'.format(oracle_conf.substitute()))
    run('source $HOME/.bashrc')
    sudo('echo {0} > /etc/ld.so.conf.d/oracle.conf'.format(oracle_dir))
    sudo('ldconfig')


@task
def sap_client():
    """ Déploiement des fichiers et packages nécessaires à l'installation du client SAP pour Python
    Cette tâche nécessite un environnement Python installé et à jour sur la machine cible et est nécessaire à
    l'installation de la librairie Python saprfc.
    """
    # required environment variables
    require('local_repository', 'ubuntu_version')
    # system libs installation
    backports_repository = "deb http://fr.archive.ubuntu.com/ubuntu {0}-backports main restricted universe multiverse"\
        .format(env.ubuntu_version)
    sudo("echo  {0} >> /etc/apt/sources.list".format(backports_repository))
    sudo("aptitude update")
    sudo("aptitude install libstdc++5")

    # destination directory
    sudo('mkdir /usr/sap')
    saprfc = "rfcsdk_64.tar.gz"
    with cd('/tmp'):
        run('wget http://{0[root]}/{0[libs]/sifac/{1}}'.format(
            env.local_repository, saprfc))
    with cd('/usr/sap'):
        sudo("tar xvf /tmp/rfcsdk_64.tar.gz")
    sudo('ln -s /usr/sap/rfcsdk/lib/librfccm.so /lib/')


@task
def tag(version):
    """ """
    env.tag = version


def build_env():
    # check if tag is specified if not prompt user
    if "tag" not in env:
        env.tag = prompt('Please specify target tag used: ')

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

    if not "releases" in env:
        if fabtoolsfiles.is_dir(env.remote_releases_path):
            env.releases = sorted(run('ls -x %(releases_path)s' %
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
