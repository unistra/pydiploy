# -*- coding: utf-8 -*-
import fabtools


def python_pkg(update=False):
    fabtools.require.deb.packages([
        'python-dev',
        'python-pip'
    ], update=update)
    fabtools.require.python.install('pip', upgrade=True, use_sudo=True)
