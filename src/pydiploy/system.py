# -*- coding: utf-8 -*-

"""
"""

import os

from fabric.api import env
from fabric.api import run
from fabtools import require


def remote_home(user):
    """
    """
    if not env.has_key('remote_home'):
        user_info = run('grep %s /etc/passwd' % user)
        env.remote_home = user_info.split(':')[5]
    return env.remote_home


