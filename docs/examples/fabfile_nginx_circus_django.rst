A simple fab file to deploy a django web app with circus/nginx using postgres and oracle
========================================================================================

.. code-block:: python

    # -*- coding: utf-8 -*-

    """
        Fabfile example file to deploy a standard django webapp
    """

    from fabric.api import (env, roles, execute, task)
    from os.path import join

    from pydiploy.prepare import tag, build_env as pydiploy_build_env
    from pydiploy.django import (deploy_backend as pydiploy_deploy_backend,
                                 deploy_frontend as pydiploy_deploy_frontend,
                                 rollback as pydiploy_rollback,
                                 post_install_backend as pydiploy_postinstall_backend,
                                 post_install_frontend as pydiploy_postinstall_frontend,
                                 pre_install_backend as pydiploy_preinstall_backend,
                                 pre_install_frontend as pydiploy_preinstall_frontend,
                                 reload_frontend as pydiploy_reload_frontend,
                                 reload_backend as pydiploy_reload_backend)

    from pydiploy.require.databases import (install_oracle_client as pydiploy_setup_oracle,
                                           install_postgres_server as pydiploy_setup_postgres)
    # edit config here !
    env.user = 'vagrant'  # user for ssh

    env.remote_owner = 'django'  # remote server user
    env.remote_group = 'di'  # remote server group

    env.application_name = 'myapp'   # name of webapp
    env.root_package_name = 'myapp'  # name of app in webapp

    env.remote_home = '/home/django'  # remote home root
    env.remote_python_version = 3.3  # python version
    env.remote_virtualenv_root = join(env.remote_home, '.virtualenvs')  # venv root
    env.remote_virtualenv_dir = join(env.remote_virtualenv_root,
                                     env.application_name)  # venv for webapp dir
    env.remote_repo_url = 'git@git.net:myapp.git'  # git repository url
    env.local_tmp_dir = '/tmp'  # tmp dir
    env.remote_static_root = 'static'  # root of static files
    env.locale = 'fr_FR.UTF-8'  # locale to use on remote
    env.timezone = 'Europe/Paris'  # timezone for remote
    env.keep_releases = 2  # number of old releases to keep before cleaning

    # optionnal parameters

    env.dest_path = '' # if not set using env_local_tmp_dir
    env.excluded_files = ['pron.jpg'] # file(s) that rsync should exclude when deploying app
    env.extra_ppa_to_install = ['ppa:vincent-c/ponysay'] # extra ppa source(s) to use
    env.extra_pkg_to_install = ['ponysay'] # extra debian/ubuntu package(s) to install on remote
    env.cfg_shared_files = ['config','/app/path/to/config/config_file'] # config files to be placed in shared config dir
    env.extra_goals = ['preprod'] # add extra goal(s) to defaults (test,dev,prod)
    env.verbose = True # verbose display for pydiploy default value = True

    env.oracle_client_version = '11.2'
    env.oracle_download_url = 'http://librepo.net/lib/oracle/'
    env.oracle_remote_dir = 'oracle_client'
    env.oracle_packages = ['instantclient-basic-linux-x86-64-11.2.0.2.0.zip',
                           'instantclient-sdk-linux-x86-64-11.2.0.2.0.zip',
                           'instantclient-sqlplus-linux-x86-64-11.2.0.2.0.zip']

    # change the package to use to install circus
    # env.circus_package_name = 'https://github.com/morganbohn/circus/archive/master.zip'

    # add directive(s) to nginx config file in location part
    # env.nginx_location_extra_directives = ['proxy_read_timeout 120']

    # fill and uncomment not to pass parameters in term
    # env.default_db_host = 'localhost'
    # env.default_db_name = 'myapp_db'
    # env.default_db_user = 'myapp_db_user'
    # env.default_db_password = 'S3CR3T'


    @task
    def test():
        """Define test stage"""
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
        env.path_to_cert_key = '/etc/ssl/private/mtapp.net.key'
        env.goal = 'prod'
        env.socket_port = '8001'
        env.map_settings = {
            #'default_db_user': "DATABASES['default']['USER']",
            #'default_db_password': "DATABASES['default']['PASSWORD']",
            #'ldap_user': "DATABASES['ldap']['USER']",
            #'ldap_password': "DATABASES['ldap']['PASSWORD']",
            #'secret_key': "SECRET_KEY"
        }
        execute(build_env)

    # dont touch after that point if you don't know what you are doing !


    @roles(['web','lb'])
    def build_env():
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
        execute(pydiploy_deploy_backend)
        execute(pydiploy_deploy_frontend)


    @roles('web')
    @task
    def deploy_backend(update_pkg=False):
        """Deploy code on server"""
        execute(pydiploy_deploy_backend)

    @roles('lb')
    @task
    def deploy_frontend():
        """Deploy static files on load balancer"""
        execute(pydiploy_deploy_frontend)

    @roles('web')
    @task
    def rollback():
        """Rollback code (current-1 release)"""
        execute(pydiploy_rollback)


    @task
    def post_install():
        """post install for backend & frontend"""
        execute(post_install_backend)
        execute(post_install_frontend)


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
    def install_postgres():
        """Install Postgres on remote"""
        execute(pydiploy_setup_postgres)


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
