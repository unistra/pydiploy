# -*- coding: utf-8 -*-
import os
import fabtools
from fabric.api import env
from pydiploy.decorators import do_verbose


@do_verbose
def deploy_environ_file():
    """ Uploads environ.py template on remote """

    fabtools.files.upload_template('environ.py',
                                   os.path.join(
                                       env.remote_base_package_dir,
                                       'environ.py'),
                                   template_dir=env.local_tmp_root_app_package,
                                   context=env,
                                   use_sudo=True,
                                   user=env.remote_owner,
                                   chown=True,
                                   mode='644',
                                   use_jinja=True)
