# -*- coding: utf-8 -*-

"""
"""


import fabtools
from fabric.api import sudo, run, env


def django_user(commands=None):
    """
    """
    fabtools.require.group(env.remote_group)
    fabtools.require.user(env.remote_owner,
                          create_home=True,
                          create_group=True,
                          group=env.remote_group,
                          shell='/bin/bash')
    if commands:
        fabtools.require.sudoer('%%%s' % env.remote_group,
                                operators='%s,root' % env.remote_owner,
                                passwd=False,
                                commands=commands)


def django_group(name):
    """
    """
    fabtools.require.group(name)


def update_pkg_index():
    fabtools.require.deb.uptodate_index(max_age={'day': 1})


def set_locale():
    """Set server's locales"""
    locale = run("echo $LANG")
    if(locale != env.locale):
        sudo('locale-gen ' + env.locale)
        sudo('/usr/sbin/update-locale LANG=' + env.locale)


def set_timezone():
    """Set the timezone"""
    if fabtools.system.distrib_id() not in('Ubuntu', 'Debian'):
        print("Cannot deploy to non-debian/ubuntu host: %s" % env.server_name)
        return

    return sudo("cp -f /usr/share/zoneinfo/%s /etc/localtime" % env.timezone)


def permissions():
    """Make the release group-writable"""
    sudo("chown -R %(user)s:%(group)s %(domain_path)s" %
         {'domain_path': env.remote_project_dir,
          'user': env.remote_owner,
          'group': env.remote_group})
    sudo("chmod -R g+w %(domain_path)s" %
         {'domain_path': env.remote_project_dir})


def symlink():
    """Updates symlink stuff to the current deployed version"""
    sudo("ln -nfs %(shared_path)s/log %(current_release)s/log" %
         {'shared_path': env.remote_shared_path,
          'current_release': env.remote_current_release})
