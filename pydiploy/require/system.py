# -*- coding: utf-8 -*-

"""
This class is for sytem relatives tools and commands

"""

from contextlib import contextmanager
import fabric
import fabtools
from fabric.api import env
from pydiploy.decorators import do_verbose


@do_verbose
def add_user(commands=None):
    """
    Creates user on remote system

    commands : string parameter to add commands in a sudoers file
    so that you could execute commands on remote system without PASSWORD: ::

        execute(your_task,commands='/usr/bin/rsync,/usr/sbin/service ipsec restart')

    here rsync and service ipsec restart could then be launch without password

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


@do_verbose
def add_group(name):
    """ Creates user's group (=name) on a remote server """

    fabtools.require.group(name)


@do_verbose
def update_pkg_index():
    """ Updates packages on remote server (ubuntu/debian) """

    fabtools.require.deb.uptodate_index(max_age={'day': 1})


@do_verbose
def set_locale():
    """
    Sets server's locales
    """
    locale = fabric.api.run("echo $LANG")
    if(locale != env.locale):
        fabric.api.sudo('locale-gen ' + env.locale)
        fabric.api.sudo('/usr/sbin/update-locale LANG=' + env.locale)


@do_verbose
def set_timezone():
    """
    Sets the timezone
    """
    if fabtools.system.distrib_id() not in('Ubuntu', 'Debian'):
        print("Cannot deploy to non-debian/ubuntu host")
        return

    if fabtools.files.is_link("/etc/localtime"):
        return fabric.api.sudo("ln -sf /usr/share/zoneinfo/%s /etc/localtime" % env.timezone)
    else:
        return fabric.api.sudo("cp -f /usr/share/zoneinfo/%s /etc/localtime" % env.timezone)


@do_verbose
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


@do_verbose
def package_installed(pkg_name):
    """
    Checks if a debian/ubuntu package is installed
    ref: http:superuser.com/questions/427318/#comment490784_427339
    """

    cmd_f = 'dpkg-query -l "%s" | grep -q ^.i'
    cmd = cmd_f % (pkg_name)
    with fabric.api.settings(warn_only=True):
        with fabric.api.quiet():
            result = fabric.api.sudo(cmd)
    return result.succeeded


@do_verbose
def check_python3_install(version='python3', update=False):
    """
    Installs python 3 on ubuntu remote server
    """

    if not package_installed(version):
        # TODO check for others ubuntu"s versions !!!!!
        if fabtools.system.distrib_id() == 'Ubuntu' and float(fabtools.system.distrib_release()) < 13.10 or float(fabtools.system.distrib_release()) >= 16.04:
            fabtools.require.deb.packages(['software-properties-common'],
                                          update=update)
            # Install mighty PPA
            fabtools.require.deb.ppa('ppa:deadsnakes/ppa')
        fabtools.require.deb.package(version, update=True)


@do_verbose
def install_extra_packages(pkg, update=False):
    """
    Installs extra packages on remote server
    """

    fabtools.require.deb.packages(pkg, update=update)


@do_verbose
def install_extra_ppa(extra_ppa):
    """

    Installs extra ppa source on remote server
    """
    for ppa in extra_ppa:
        fabtools.require.deb.ppa(ppa)


@do_verbose
def is_systemd():
    """ Returns True if systemd is used """
    return fabtools.files.is_dir("/run/systemd/system")


@do_verbose
def install_extra_source(extra_source):
    """

    Installs extra debian source on remote server
    """
    for source in extra_source:
        fabtools.require.deb.source(*source)


@contextmanager
def shell(new_shell):
    old_shell, env.shell = env.shell, new_shell
    yield
    env.shell = old_shell
