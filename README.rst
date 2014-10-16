pydiploy
========
.. image:: https://secure.travis-ci.org/unistra/pydiploy.png?branch=master
    :target: https://travis-ci.org/unistra/pydiploy

.. image:: http://coveralls.io/repos/unistra/pydiploy/badge.png?branch=master
    :target: http://coveralls.io/r/unistra/pydiploy?branch=master

Pydiploy is a library used to deal with administration and deployment of applications on several environments (i.e : dev, test, pre-production, production) The library is based on fabric and fabtools.
The purpose of the project is to deliver bunch of tools as generic as possible to standardize deployments and administrations tasks.
To use it : create a fabfile (fabfile.py or fabfile/__init__.py) and start playing with your new toy !


Install
-------

    - Requirements : python2.7, fabtools and fabric
    - Installation : pip install pydiploy

Usage
-----

    - See the example in the doc to setup correctly a fabfile (fabric,fabtools and pydiploy should be installed)
    - Use following command to install/deploy an application in test stage : ::

        fab tag:master test pre_install deploy post_install

    - Just remember that the tag parameter is just used for the 'deploy' task if not set pydiploy will prompt you to choose a tag.
    - Use following command to install/deploy an application in production stage : ::

        fab tag:master prod pre_install deploy post_install
    - To deploy a new tag/release on production stage : ::

        fab tag:1.0.1 prod deploy
    - if something went wrong during deploy process you could rollback previous release : ::

        fab prod rollback
    - To deploy with arguments : ::

        fab tag:master test --set default_db_host='localhost',default_db_name='mydb',default_db_user='myuser',default_db_password='mypass' deploy

    - See fabric documentation for more infos : http://fabric.readthedocs.org

Tips
----

.. _`databases`:

Databases
~~~~~~~~~

    - django+sqlite3 : if you use sqlite3 with django, don't put your .db file in the same folder as your application. It will be erased for each deployement !

    - Specific oracle installation optional settings : ::

        env.oracle_client_version = '11.2'
        env.oracle_download_url = 'http://librepo.net/lib/oracle/'
        env.oracle_remote_dir = 'oracle_client'
        env.oracle_packages = ['instantclient-basic-linux-x86-64-11.2.0.2.0.zip',
                               'instantclient-sdk-linux-x86-64-11.2.0.2.0.zip',
                               'instantclient-sqlplus-linux-x86-64-11.2.0.2.0.zip']

.. _`maintenance-mode`:

Maintenance mode
~~~~~~~~~~~~~~~~

    - For a django webapp deployement you can set the webserver to be in maintenance mode before deploying. For that purpose you could import in your fabfile pydiploy.django.set_app_up and pydiploy.django.set_app_down in a task :

      .. code-block:: python
          :emphasize-lines: 1,2,7,9,14,16

          from pydiploy.django import (set_app_up as pydiploy_set_up,
                                       set_app_down as pydiploy_set_down)


          @roles('web_server_role')
          @task
          def set_down():
              """ Set app to maintenance mode """
              execute(pydiploy_set_down)


          @roles('web_server_role')
          @task
          def set_up():
              """ Set app to up mode """
              execute(pydiploy_set_up)

    - Then you could call directly the new tasks to toggle between up and down mode a maintenance.html will be used rendered with a 503 http status

    - Toggle to maintenance mode and active maintenance page : ::

        fab prod set_down

    - When setting the site in maintenance mode you could customize title and text of the maintenance page : ::

        fab prod set_down --set maintenance_title='Webapp is down !',maintenance_text='Time for maintenance, please come back later'

    - If you want to permanent change the default maintenance page you could set an env var in fabfile :

      .. code-block:: python
          :emphasize-lines: 3,4

          # Put this somewhere in the fabfile

          env.maintenance_title='Webapp is down !'
          env.maintenance_text='Time for maintenance, please come back later'

    - Toggle to up mode and deactivate maintenance page : ::

        fab prod set_up

Optional parmeters
~~~~~~~~~~~~~~~~~~

    - dest_path specifies a local temp dir if dest_path not set /tmp is used : ::

        env.dest_path = '/home/myuser/deploy/tmp'

    - excluded_files used to specify files that should be excluded when deploying app for files that are not in .gitignore file : ::

        env.excluded_files = ['config.py-DIST','README.rst']

    - extra_ppa_to_install adds extra(s) ppa's sourc(e)s when setting server : ::

        extra_ppa_to_install = ['ppa:vincent-c/ponysay']

    - extra_pkg_to_install adds extra(s) package(s) when setting server : ::

        env.extra_pkg_to_install = ['ponysay','cowsay']

    - cfg_shared_files puts configuration's file(s) in shared directory on remote server. File(s) will be 'symlinked' from shared to current directory : ::

        env.cfg_shared_files = ['/app/path/to/config/config_file']

    - extra_symlink_dirs puts extra(s) dir(s) to shared directory : ::

        env.extra_symlink_dirs = ['mydir','/app/mydir']

    - extra_goals adds extra(s) goal to defaults test,dev,prod stages : ::

        env.extra_goals = ['preprod','customer-preprod']

    - verbose True by default if False the configuration checker will not lists whole parameters : ::

        env.verbose = False

    - req_pydiploy_version could be used to require a pydiploy version installed for fabfile file. Pydiploy will check that version installed is not too recent for fabfile provided comparing pydiploy version x.x on version req_pydiploy_version : ::

        env.req_pydiploy_version = "1.0"

    - no_config_test if True it disables the check of configuration (required env vars...) be carefull if you set it TRUE : ::

        env.no_config_test = True

    - maintenance_title and maintenance_text : see :ref:`maintenance-mode` : ::

        env.maintenance_title='Webapp is down !'
        env.maintenance_text='Time for maintenance, please come back later'

    - circus_package_name provides an alternate repository url for specific circus package : ::

        env.circus_package_name = 'https://github.com/githubaccount/circus/archive/master.zip'

    - nginx_location_extra_directives adds specific directives in location part of nginx config file : ::

        env.nginx_location_extra_directives = ['proxy_read_timeout 120']

    - oracle_* : see :ref:`databases`


