# -*- coding: utf-8 -*-

"""
Oracle
======

Required functions for Oracle database

"""

import os
from string import Template

import fabric
import fabtools
from fabric.api import env
from pydiploy.decorators import do_verbose


@do_verbose
def install_oracle_client():
    """
    installs oracle's specif client for Python oracle_cx for example.

    needed env vars in fabfile:

    * env.oracle_client_version eg : '11.2.0.2.0'
    * env.oracle_download_url : eg 'http://libshost/lib/oracle_repo/''
    * env.oracle_remote_dir : name of oracle installation directore eg : 'oracle_client'
    * env.oracle_packages : name(s) of zip file(s) for oracle's packages to deploy

    """
    if all([e in env.keys() for e in ('oracle_client_version',
                                      'oracle_download_url',
                                      'oracle_remote_dir',
                                      'oracle_packages')]):

        # system libs and goodies installation
        fabtools.require.deb.packages(['libaio-dev', 'unzip'])

        fabtools.require.files.directory(
            path=os.path.join(env.remote_home, env.oracle_remote_dir),
            use_sudo=True,
            owner=env.remote_owner,
            group=env.remote_group,
            mode='750')

        # get oracle's zip file(s) and unzip
        with fabric.api.cd(env.remote_home):
            for package in env.oracle_packages:
                fabric.api.sudo('wget -c %s%s' %
                                (env.oracle_download_url, package))
                fabric.api.sudo('unzip %s -d %s' %
                                (package, env.oracle_remote_dir))
                fabric.api.sudo(
                    'rm %s' % os.path.join(env.remote_home, package))

            oracle_dir = 'instantclient_%s' % '_'.join(
                env.oracle_client_version.split('.')[:2])
            oracle_root_path = os.path.join(env.oracle_remote_dir, oracle_dir)
            oracle_full_path = os.path.join(env.remote_home, oracle_root_path)

            with fabric.api.cd(oracle_root_path):
                if not fabtools.files.is_link('libclntsh.so', use_sudo=True):
                    fabric.api.sudo('ln -s libclntsh.so.* libclntsh.so')

            # library configuration
            oracle_conf = Template(
                "# ORACLE CLIENT CONFIGURATION"
                "\nexport ORACLE_HOME=$oracle_dir"
                "\nexport LD_LIBRARY_PATH=$$LD_LIBRARY_PATH:$$ORACLE_HOME"
            )

            fabric.api.sudo('pwd')
            fabric.api.sudo('echo \'%s\' >> .bashrc' %
                            oracle_conf.substitute(oracle_dir=oracle_full_path))
            fabric.api.sudo('source .bashrc')
            fabric.api.sudo(
                'echo %s > /etc/ld.so.conf.d/oracle.conf' % oracle_full_path)
            fabric.api.sudo('ldconfig')
    else:
        fabric.api.abort('Please provide parameters for oracle installation !')


@do_verbose
def install_oracle_jdk(version='7u25-b15'):
    """ install oracle jdk from oracle website """
    fabtools.oracle_jdk.install_from_oracle_site(version=version)


@do_verbose
def get_oracle_jdk_version():
    """ get oracle jdk version returns null if not installed """
    return fabtools.oracle_jdk.version()
