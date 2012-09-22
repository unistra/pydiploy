"""
"""

from fabric.api import env
from fabric.api import exists
from fabric.api import cd
from fabric.api import run

import fabtools
from fabtools import require


def install(tmp_directory):
    """
    """
    with fabtools.python.virtualenv(env.virtualenv_dir):
        with cd(tmp_directory):
            run('python setup.py install')
            if exists('requirements/%s.txt' % env.env):
                require.python.requirements('requirements/%s.txt' % env.env)
