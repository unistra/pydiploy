# -*- coding: utf-8 -*-

"""
    Fabfile example file to deploy a standard simple webapp
"""

from fabric.api import (env, roles, execute, task)
from os.path import join

from pydiploy.prepare import (tag as pydiploy_tag,
                              build_env as pydiploy_build_env)
from pydiploy.simple import (deploy_backend as pydiploy_deploy_backend,
                             rollback as pydiploy_rollback,
                             post_install_backend as pydiploy_postinstall_backend,
                             pre_install_backend as pydiploy_preinstall_backend)

# edit config here !

env.use_sudo = True # use sudo or not

env.remote_owner = 'myremoteuser'
env.remote_group = 'myremotegroup'

env.application_name = 'myapp'
env.root_package_name = 'myapp'

env.remote_home = '/home/myremoteuser'  # remote home root
env.remote_python_version = 3.4  # python version
env.remote_virtualenv_root = join(env.remote_home, '.virtualenvs')  # venv root
env.remote_virtualenv_dir = join(env.remote_virtualenv_root,
                                 env.application_name)  # venv for webapp dir

env.remote_repo_url = 'git@git.net:myapp.git'
env.local_tmp_dir = '/tmp'  # tmp dir
env.locale = 'fr_FR.UTF-8'  # locale to use on remote
env.timezone = 'Europe/Paris'  # timezone for remote
env.keep_releases = 2  # number of old releases to keep before cleaning

# optional parameters

env.application_type = 'simple'  # specify another type of application

# env.remote_repo_specific_folder = '' # specify a subfolder for the remote repository
# env.user = 'my_user'  # user for ssh
# env.dest_path = '' # if not set using env_local_tmp_dir
# env.excluded_files = ['pron.jpg'] # file(s) that rsync should exclude when deploying app
# env.extra_ppa_to_install = ['ppa:vincent-c/ponysay'] # extra ppa source(s) to use
# env.extra_pkg_to_install = ['ponysay'] # extra debian/ubuntu package(s) to install on remote
# env.extra_source_to_install = [['mongodb', 'http://downloads-distro.mongodb.org/repo/ubuntu-upstart', 'dist', '10gen'], ['deb-src', 'http://site.example.com/debian', 'distribution', 'component1', 'component2', 'component3']]
# env.cfg_shared_files = ['config','/app/path/to/config/config_file'] # config files to be placed in shared config dir
# env.extra_symlink_dirs = ['mydir','/app/mydir'] # dirs to be symlinked in shared directory
# env.extra_goals = ['preprod'] # add extra goal(s) to defaults (test,dev,prod)
# env.verbose = True # verbose display for pydiploy default value = True
env.req_pydiploy_version = '1.1.5.0'  # required pydiploy version for this fabfile

# env.run_tests_command = 'tox'

# fill and uncomment not to pass parameters in term (eg: fab tag:master test --set default_db_host='localhost',default_db_name='my_app_db' )
# env.default_db_host = 'localhost'
# env.default_db_name = 'myapp_db'
# env.default_db_user = 'myapp_db_user'
# env.default_db_password = 'S3CR3T'


@task
def test():
    """Define test stage"""
    env.user = 'vagrant'
    env.roledefs = {
        'web': ['192.168.1.4']
    }
    env.goal = "test"
    # env.server_name = "myapp.net"  # optional: if you want to use an url for the name of the remote app folder instead of the application name (manual bottle or flask app)
    env.map_settings = {
        # uncomment to use :
        #'ldap_user': "DATABASES['ldap']['USER']",
        #'ldap_password': "DATABASES['ldap']['PASSWORD']"
    }
    execute(build_env)

@task
def prod():
    """Define prod stage"""
    env.roledefs = {
        'web': ['myserver.net']
    }
    env.goal = "prod"
    # env.server_name = "myapp.net"  # optional: if you want to use an url for the name of the remote app folder instead of the application name (manual bottle or flask app)
    env.map_settings = {
        # uncomment to use :
        #'ldap_user': "DATABASES['ldap']['USER']",
        #'ldap_password': "DATABASES['ldap']['PASSWORD']"
    }
    execute(build_env)

# dont touch after that point if you don't know what you are doing !


@task
def tag(version_string):
    """ Set the version to deploy to `version_number`. """
    execute(pydiploy_tag, version=version_string)


@task
def head_master():
    """ Set the version to deploy to the head of the master. """
    execute(pydiploy_tag, version='master')


@roles(['web'])
def build_env():
    """ Build the deployment environnement. """
    execute(pydiploy_build_env)


@task
def pre_install():
    """ Pre install of backend & frontend. """
    execute(pre_install_backend)


@roles('web')
@task
def pre_install_backend():
    """ Setup server for backend. """
    execute(pydiploy_preinstall_backend, commands='/usr/bin/rsync')


@task
def deploy():
    """Deploy code and sync static files"""
    execute(deploy_backend)


@roles('web')
@task
def deploy_backend(update_pkg=False):
    """Deploy code on server"""
    execute(pydiploy_deploy_backend, update_pkg)


@roles('web')
@task
def rollback():
    """ Rollback code (current-1 release). """
    execute(pydiploy_rollback)


@task
def post_install():
    """ Post install for backend & frontend. """
    execute(post_install_backend)


@roles('web')
@task
def post_install_backend():
    """ Post installation of backend. """
    execute(pydiploy_postinstall_backend)
