# -*- coding: utf-8 -*-

"""
"""

from fabric.api import env, run


def remote_home(user):
    """
    """
    if not env.has_key('remote_home'):
        user_info = run('grep %s /etc/passwd' % user)
        env.remote_home = user_info.split(':')[5]
    return env.remote_home
