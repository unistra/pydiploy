# -*- coding: utf-8 -*-

"""
"""


import fabtools
import fabric
from fabric.api import env


def django_user(commands=None):
    """
    Creates django user on remote system

    commands is a string parameter to add commands in a sudoers file so that
    you could execute commands on remote system without PASSWORD:

    ex :

    execute(your_task,commands='/usr/bin/rsync,/usr/sbin/service ipsec restart')

    here rsync and service ipsec restart are launch without password

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
    Creates user (name) group for the web app
    """
    fabtools.require.group(name)


def update_pkg_index():
    """
    Updates packages on remote server (ubuntu/debian)
    """
    fabtools.require.deb.uptodate_index(max_age={'day': 1})


def set_locale():
    """
    Sets server's locales
    """
    locale = fabric.api.run("echo $LANG")
    if(locale != env.locale):
        fabric.api.sudo('locale-gen ' + env.locale)
        fabric.api.sudo('/usr/sbin/update-locale LANG=' + env.locale)


def set_timezone():
    """
    Sets the timezone
    """
    if fabtools.system.distrib_id() not in('Ubuntu', 'Debian'):
        print("Cannot deploy to non-debian/ubuntu host: %s" % env.server_name)
        return

    return fabric.api.sudo("cp -f /usr/share/zoneinfo/%s /etc/localtime" % env.timezone)


def permissions():
    """
    Makes the release group-writable
    """
    fabric.api.sudo("chown -R %(user)s:%(group)s %(domain_path)s" %
                    {'domain_path': env.remote_project_dir,
                     'user': env.remote_owner,
                     'group': env.remote_group})
    fabric.api.sudo("chmod -R g+w %(domain_path)s" %
                    {'domain_path': env.remote_project_dir})


def package_installed(pkg_name):
    """
    checks if a debian/ubuntu package is installed
    ref: http:superuser.com/questions/427318/#comment490784_427339
    """
    cmd_f = 'dpkg-query -l "%s" | grep -q ^.i'
    cmd = cmd_f % (pkg_name)
    with fabric.api.settings(warn_only=True):
        with fabric.api.quiet():
            result = fabric.api.sudo(cmd)
    return result.succeeded


def check_python3_install(version='python3', update=False):
    """
    Installs python 3 on ubuntu remote server
    """
    if not package_installed(version):
        if fabtools.system.distrib_id() == 'Ubuntu' and float(fabtools.system.distrib_release()) < 13.10:
            fabtools.require.deb.packages(['python-software-properties'],
                                          update=update)
            fabtools.require.deb.ppa('ppa:fkrull/deadsnakes')
        fabtools.require.deb.package(version, update=True)
