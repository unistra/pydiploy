"""
"""


import fabtools
from pydiploy.require import groups


def django_user():
    """
    """
    groups.create('di')
    groups.create('admin')
    if not fabtools.user.exists('django'):
        fabtools.user.create('django', home='/home/django', groups=['di',
        'admin'])
    fabtools.require.files.directory('/home/django', use_sudo=True,
            owner='django', group='di')


def django_group(no_check=False):
    """
    """
    groups.create('di')
    groups.create('admin')
