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
from fabric.api import env, cd, require, run, sudo, task
from fabric.api import cd
from fabric.api import require
from fabric.api import run
from fabric.api import sudo
from fabric.api import task


# def setuptools():
#     """ Installation des libraires d'installation de librairies Python depuis des dépôts centraux comme `Pypi
#     <pypi.python.org>`_ ou locaux comme `repodipory <http://repodipory.u-strasbg.fr/lib/python>`_, ou des dépôts de
#     code comme GitHub. Les commandes `pip <http://www.pip-installer.org/en/latest/usage.html>`_ et
# `easy_install <http://peak.telecommunity.com/DevCenter/EasyInstall#using-easy-install>`_ seront alors disponibles.
#     """
#     sudo("aptitude install python-setuptools")
#     sudo("easy_install pip")


# def virtualenv():
#     """ Installation ou mise jour des outils `virtualenv <http://www.virtualenv.org/en/latest/index.html>`_ et
#     `virtualenvwrapper <http://www.doughellmann.com/projects/virtualenvwrapper/>`_
#     """
#     sudo("pip install -U virtualenv virtualenvwrapper")


# def update_bashrc():
#     """ Met à jour le fichier bashrc afin de prendre en compte le fichier .bash_profile dans le shell de l'utilisateur.
#     """
#     bashrc_profile = Template(""
#                               "if [ -f ~/.bash_profile ]; then"
#                               "    . ~/.bash_profile"
#                               "fi")
#     run('echo %s >> $HOME/.bashrc' % bashrc_profile)
#     run('touch $HOME∕.bash_profile')
#     run('source $HOME/.bashrc')


# def generate_bash_profile():
#     """ Génération du fichier de profil Bash pour permettre l'activation des fonctionnalités de virtualenwrapper.
#     """
#     require('virtualenvs_path')
#     bash_profile = Template(
#         "export WORKON_HOME=$env_root_path\n"
#         "export PIP_RESPECT_VIRTUALENV=true\n"
#         "source /usr/local/bin/virtualenvwrapper.sh"
#     )
#     run('echo "%s" >> $HOME/.bash_profile' %
#         bash_profile.substitute(env_root_path=env.virtualenvs_path))


# @task
# def install_tools():
#     """ Installation d'outils de base:

#     * unzip
#     """
#     sudo('aptitude install unzip')


# @task
# def update_python_env():
#     """ Mise à jour de l'environnement Python.
#     """
#     sudo("pip install -U pip")
#     virtualenv()


# @task
# def create_python_env():
#     """ Création de l'environnement Python.
#     """
#     setuptools()
#     sudo('aptitude install python-dev')
#     virtualenv()
#     generate_bash_profile()


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
