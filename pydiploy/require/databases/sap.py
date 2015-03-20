# -*- coding: utf-8 -*-

"""
Oracle
======

Required functions for Oracle database

"""

from os.path import join, sep

import fabric
import fabtools
from fabric.api import env
from pydiploy.decorators import do_verbose


@do_verbose
def install_sap_client():
    """
    installs sap's specif client for Python saprfc for example.

    needed env vars in fabfile:

    * env.sap_download_url : eg 'http://libshost/lib/oracle_repo/''
    * env.sap_packages : name(s) of zip file(s) for oracle's packages to deploy

    """
    sap_lib_path = join(sep, 'usr', 'sap')

    if all([e in env.keys() for e in ('sap_download_url',
                                      'sap_packages')]):

        # system libs and goodies installation
        fabtools.require.deb.packages(['libstdc++5'])

        fabtools.require.files.directory(path=sap_lib_path,
                                         use_sudo=True,
                                         mode='755')

        # get oracle's zip file(s) and unzip
        with fabric.api.cd(sap_lib_path):
            for package in env.sap_packages:
                fabric.api.sudo('wget -c %s%s' %
                                (env.sap_download_url, package))
                fabric.api.sudo('tar xvf %s' % package)
                fabric.api.sudo('chmod -R 755 rfcsdk')
                fabric.api.sudo('rm %s' % package)

            with fabric.api.cd(join(sep, 'lib')):
                if not fabtools.files.is_link('librfccm.so', use_sudo=True):
                    fabric.api.sudo('ln -s %s .' % join(sap_lib_path, 'rfcsdk',
                                                        'lib', 'librfccm.so'))

    else:
        fabric.api.abort('Please provide parameters for sap installation !')
