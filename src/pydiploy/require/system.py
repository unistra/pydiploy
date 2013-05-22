"""
"""


import fabtools
from pydiploy.require import groups


def django_user(name, group_name):
    """
    """
    fabtools.require.user(name, create_home=True, create_group=False,
            group=group_name, shell='/bin/bash')


def django_group(name):
    """
    """
    fabtools.require.group(name)
