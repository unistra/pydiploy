"""
"""

from fabric.api import env
from fabric.api import cd
from fabric.api import run
from fabric.contrib.files import exists

import fabtools
from fabtools import require


def install(tmp_directory):
    """
    """
    require.python.distribute()
    require.python.pip()
    require.python.virtualenv(env.virtualenv_dir,
            python='/usr/bin/python%s' % env.python_version)
    with fabtools.python.virtualenv(env.virtualenv_dir):
        with cd(tmp_directory):
            run('python setup.py install')
            if exists('requirements/%s.txt' % env.env):
                require.python.requirements('requirements/%s.txt' % env.env)
