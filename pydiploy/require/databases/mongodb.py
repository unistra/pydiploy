# -*- coding: utf-8 -*-

"""
Mongodb
=======


Requires functions for mongodb database
"""

import fabric
import fabtools
import pydiploy
from pydiploy.decorators import do_verbose


@do_verbose
def install_mongodb():
    if not pydiploy.require.system.package_installed('mongodb-10gen'):
        fabtools.require.deb.source('mongodb',
                                    'http://downloads-distro.mongodb.org/repo/ubuntu-upstart',
                                    'dist', '10gen')

        fabric.api.sudo('apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 7F0CEB10')
        fabtools.require.deb.uptodate_index(quiet=True)
        fabtools.require.deb.package('mongodb-10gen')
