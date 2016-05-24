# -*- coding: utf-8 -*-

""" This module is used for commands relatives to bottle framework

"""

import os

import fabric
import fabtools
from fabric.api import env
from pydiploy.decorators import do_verbose


@do_verbose
def bottle_prepare():
    """
    Prepares bottle webapp (collect statics)
    """

    # remove old statics from local tmp dir before collecting new ones
    with fabric.api.lcd(env.local_tmp_dir):
        fabric.api.local('rm -rf assets/*')

    # simulate collect static
    with fabtools.python.virtualenv(env.remote_virtualenv_dir):
        with fabric.api.cd(env.remote_current_path):
            with fabric.api.settings(sudo_user=env.remote_owner):
                    fabric.api.sudo('cp -R %s/static assets' % env.root_package_name)

    fabric.api.get(os.path.join(env.remote_current_path, 'assets'),
                   local_path=env.local_tmp_dir)
