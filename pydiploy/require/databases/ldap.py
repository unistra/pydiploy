# -*- coding: utf-8 -*-

"""
ldap
====

Requires functions for ldap

"""

import fabtools
from pydiploy.decorators import do_verbose


@do_verbose
def ldap_pkg(use_sudo=False, user=None):
    """ Installs ldap packages and dependencies """

    fabtools.require.deb.package('libldap2-dev', update=True)
    fabtools.require.deb.package('libsasl2-dev', update=True)
    fabtools.require.deb.package('libssl-dev', update=True)
    fabtools.require.python.package(
        'python-ldap', upgrade=True, use_sudo=use_sudo,
        user=user)
