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
    from pydiploy.django import (pre_install_django_app_nginx_circus,
                                 deploy as diploy,
                                 rollback as pydiploy_rollback,
                                 post_install as pydiploy_postinstall)

    from pydiploy.require.database import (install_oracle_client as pydiploy_setup_oracle,
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

    env.oracle_client_version = '11.2'
    env.oracle_download_url = 'http://librepo.net/lib/oracle/'
    env.oracle_remote_dir = 'oracle_client'
    env.oracle_packages = ['instantclient-basic-linux-x86-64-11.2.0.2.0.zip',
                           'instantclient-sdk-linux-x86-64-11.2.0.2.0.zip',
                           'instantclient-sqlplus-linux-x86-64-11.2.0.2.0.zip']

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
        }
        env.backends = ['127.0.0.1']
        env.server_name = 'myapp-dev.net'
        env.short_server_name = 'myapp-dev'
        env.server_ip = ''
        env.server_ssl_on = False
        env.goal = 'test'
        env.socket_port = '8001'
        env.socket_host = '192.168.1.2'
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
        }
        env.backends = env.roledefs['web']
        env.server_name = 'myapp.net'
        env.short_server_name = 'myapp'
        env.server_ip = ''
        env.server_ssl_on = True
        env.goal = 'prod'
        env.socket_port = '8001'
        env.socket_host = ''
        env.map_settings = {
            #'default_db_user': "DATABASES['default']['USER']",
            #'default_db_password': "DATABASES['default']['PASSWORD']",
            #'ldap_user': "DATABASES['ldap']['USER']",
            #'ldap_password': "DATABASES['ldap']['PASSWORD']",
            #'secret_key': "SECRET_KEY"
        }
        execute(build_env)

    # dont touch after that point if you don't know what you are doing !


    @roles('web')
    def build_env():
        execute(pydiploy_build_env)


    @roles('web')
    @task
    def setup_server(update_pkg=False, clear_venv=False):
        """Setup server for futur deployement"""
        execute(pre_install_django_app_nginx_circus, commands='/usr/bin/rsync')


    @roles('web')
    @task
    def deploy(update_pkg=False):
        """Deploy code on server"""
        execute(diploy)


    @roles('web')
    @task
    def rollback():
        """Rollback code (current-1 release)"""
        execute(pydiploy_rollback)


    @roles('web')
    @task
    def post_install():
        """Post installation"""
        execute(pydiploy_postinstall)


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
