# -*- coding: utf-8 -*-

"""
    Fabfile example file to deploy a standard bottle webapp
"""

from fabric.api import (env, roles, execute, task)
from os.path import join

from pydiploy.prepare import (tag as pydiploy_tag,
                              build_env as pydiploy_build_env)
from pydiploy.bottle import (deploy_backend as pydiploy_deploy_backend,
                             deploy_frontend as pydiploy_deploy_frontend,
                             rollback as pydiploy_rollback,
                             post_install_backend as pydiploy_postinstall_backend,
                             post_install_frontend as pydiploy_postinstall_frontend,
                             pre_install_backend as pydiploy_preinstall_backend,
                             pre_install_frontend as pydiploy_preinstall_frontend,
                             reload_frontend as pydiploy_reload_frontend,
                             reload_backend as pydiploy_reload_backend,
                             set_app_up as pydiploy_set_up,
                             set_app_down as pydiploy_set_down,
                             install_oracle_client as pydiploy_setup_oracle,
                             install_postgres_server as pydiploy_setup_postgres)

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
env.remote_static_root = '/var/www/static'  # root of static files
env.local_tmp_dir = '/tmp'  # tmp dir
env.locale = 'fr_FR.UTF-8'  # locale to use on remote
env.timezone = 'Europe/Paris'  # timezone for remote
env.keep_releases = 2  # number of old releases to keep before cleaning

# optional parameters

env.application_type = 'bottle'  # specify another type of application
env.req_pydiploy_version = '1.1.6.0'

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
# env.no_config_test = False # avoid config checker if True
# env.maintenance_text = "" # add a customize maintenance text for maintenance page
# env.maintenance_title = "" # add a customize title for maintenance page

# env.oracle_client_version = '11.2'
# env.oracle_download_url = 'http://librepo.net/lib/oracle/'
# env.oracle_remote_dir = 'oracle_client'
# env.oracle_packages = ['instantclient-basic-linux-x86-64-11.2.0.2.0.zip',
#                        'instantclient-sdk-linux-x86-64-11.2.0.2.0.zip',
#                        'instantclient-sqlplus-linux-x86-64-11.2.0.2.0.zip']


# env.circus_package_name = 'https://github.com/githubaccount/circus/archive/master.zip' # change the package to use to install circus
# env.no_circus_web = True # true if you don't want circus-web
# env.circus_backend = 'gevent' # name of circus backend to use

# env.chaussette_backend = 'waitress' # name of chaussette backend to use. You need to add this backend in the app requirement file.

# env.nginx_location_extra_directives = ['proxy_read_timeout 120'] # add directive(s) to nginx config file in location part
# env.nginx_force_start = True # if True, it forces to start nginx when nginx is not started

# env.socket_host='localhost' # use it in env method to force a socket host

# env.run_tests_command = 'tox'

# env.media_folder = '/media' # path of the application's media files
# env.remote_media_folder = '/srv/media/myapp' # remote folder of the application's media files

# fill and uncomment not to pass parameters in term (eg: fab tag:master test --set default_db_host='localhost',default_db_name='my_app_db' )
# env.default_db_host = 'localhost'
# env.default_db_name = 'myapp_db'
# env.default_db_user = 'myapp_db_user'
# env.default_db_password = 'S3CR3T'


@task
def test():
    """Define test stage"""
    env.user = 'vagrant'  # user for ssh
    env.roledefs = {
        'web': ['192.168.1.2'],
        'lb': ['192.168.1.3'],
    }
    env.backends = env.roledefs['web']
    env.server_name = 'myapp-dev.net'
    env.short_server_name = 'myapp-dev'
    env.static_folder = '/site_media/'
    env.server_ip = '192.168.1.3'
    env.no_shared_sessions = False
    env.server_ssl_on = False
    env.goal = 'test'
    env.socket_port = '8001'
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
        'web': ['myapp.net'],
        'lb': ['lb.myapp.net'],
    }
    env.backends = env.roledefs['web']
    env.server_name = 'myapp.net'
    env.short_server_name = 'myapp'
    env.static_folder = '/site_media/'
    env.server_ip = ''
    env.no_shared_sessions = False
    env.server_ssl_on = True
    env.path_to_cert = '/etc/ssl/certs/myapp.net.pem'
    env.path_to_cert_key = '/etc/ssl/private/myapp.net.key'
    env.goal = 'prod'
    env.socket_port = '8001'
    env.map_settings = {
        # uncomment to use :
        #'default_db_user': "DATABASES['default']['USER']",
        #'default_db_password': "DATABASES['default']['PASSWORD']",
        #'ldap_user': "DATABASES['ldap']['USER']",
        #'ldap_password': "DATABASES['ldap']['PASSWORD']",
        #'secret_key': "SECRET_KEY"
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
    """Pre install of backend & frontend"""
    execute(pre_install_backend)
    execute(pre_install_frontend)


@roles('web')
@task
def pre_install_backend():
    """Setup server for backend"""
    execute(pydiploy_preinstall_backend, commands='/usr/bin/rsync')


@roles('lb')
@task
def pre_install_frontend():
    """Setup server for frontend"""
    execute(pydiploy_preinstall_frontend)


@task
def deploy():
    """Deploy code and sync static files"""
    # uncomment this to set app in maitenance mode :
    # execute(set_down)
    execute(deploy_backend)
    execute(deploy_frontend)
    # uncomment this to toggle app to up mode again :
    #execute(set_up)


@roles('web')
@task
def deploy_backend(update_pkg=False):
    """Deploy code on server"""
    execute(pydiploy_deploy_backend, update_pkg)


@roles('lb')
@task
def deploy_frontend():
    """Deploy static files on load balancer"""
    execute(pydiploy_deploy_frontend)


@roles('web')
@task
def rollback():
    """ Rollback code (current-1 release). """
    execute(pydiploy_rollback)


@task
def post_install():
    """Post install for backend & frontend"""
    execute(post_install_frontend)
    execute(post_install_backend)


@roles('web')
@task
def post_install_backend():
    """Post installation of backend"""
    execute(pydiploy_postinstall_backend)


@roles('lb')
@task
def post_install_frontend():
    """Post installation of frontend"""
    execute(pydiploy_postinstall_frontend)

@roles('web')
@task
def install_oracle():
    """Install Oracle client on remote"""
    execute(pydiploy_setup_oracle)


@roles('web')
@task
def install_postgres(user=None, dbname=None, password=None):
    """Install Postgres on remote"""
    execute(pydiploy_setup_postgres, user=user, dbname=dbname, password=password)


@task
def reload():
    """Reload backend & frontend"""
    execute(reload_frontend)
    execute(reload_backend)


@roles('lb')
@task
def reload_frontend():
    execute(pydiploy_reload_frontend)


@roles('web')
@task
def reload_backend():
    execute(pydiploy_reload_backend)


@roles('lb')
@task
def set_down():
    """ Set app to maintenance mode """
    execute(pydiploy_set_down)


@roles('lb')
@task
def set_up():
    """ Set app to up mode """
    execute(pydiploy_set_up)
