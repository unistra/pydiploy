Pydiploy
========

.. image:: https://badges.gitter.im/Join%20Chat.svg
   :alt: Join the chat at https://gitter.im/unistra/pydiploy
   :target: https://gitter.im/unistra/pydiploy?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge

.. image:: https://secure.travis-ci.org/unistra/pydiploy.png?branch=master
    :target: https://travis-ci.org/unistra/pydiploy
    :alt: Build

.. image:: http://coveralls.io/repos/unistra/pydiploy/badge.png?branch=master
    :target: http://coveralls.io/r/unistra/pydiploy?branch=master
    :alt: Coverage

.. image:: https://img.shields.io/pypi/v/pydiploy.svg
    :target: https://pypi.python.org/pypi/pydiploy
    :alt: Version

.. image:: https://img.shields.io/pypi/pyversions/pydiploy.svg
    :target: https://pypi.python.org/pypi/pydiploy
    :alt: Python Version

.. image:: https://img.shields.io/pypi/status/pydiploy.svg
    :target: https://pypi.python.org/pypi/pydiploy
    :alt: Status

.. image:: https://img.shields.io/pypi/l/pydiploy.svg
    :target: https://docs.python.org/2/license.html
    :alt: Licence

.. image:: https://img.shields.io/pypi/dm/pydiploy.svg
    :target: https://pypi.python.org/pypi/pydiploy
    :alt: Download

.. image:: https://landscape.io/github/unistra/pydiploy/master/landscape.svg?style=flat
  :target: https://landscape.io/github/unistra/pydiploy/master
  :alt: Code Health

`Pydiploy` is a library used to deal with administration and deployment of applications on several environments (i.e : dev, test, pre-production, production) The library is based on fabric and fabtools.
The purpose of the project is to deliver bunch of tools as generic as possible to standardize deployments and administrations tasks.
To use it : create a fabfile (fabfile.py or fabfile/__init__.py) and start playing with your new toy !

Currently, it only works with :

* django applications based on the `django-drybones <https://github.com/unistra/django-drybones>`_ template (default).
* simple python applications based on the `simple-python-drybones <https://github.com/unistra/simple-python-drybones>`_ template.
* bottle applications based on the `bottle-drybones <https://github.com/unistra/bottle-drybones>`_ template.

Install
-------

    - Requirements : python2.7, fabtools, fabric and a application based on django-drybones, simple-python-drybones or bottle-drybones

    - Installation : ::

        $ pip install pydiploy

Usage
-----

    - See the example in the doc to setup correctly a fabfile (fabric,fabtools and pydiploy should be installed)

    - If env.user is not defined in fabfile (stage part or in main part of the fabfile) you can pass its value by command line : ::

        $ fab test pre_install -u your_user

    - Use following command to install/deploy an application in test stage : ::

        $ fab tag:master test pre_install deploy post_install

    - Just remember that the tag parameter is just used for the 'deploy' task if not set pydiploy will prompt you to choose a tag.

    - Use following command to install/deploy an application in production stage : ::

        $ fab tag:master prod pre_install deploy post_install

    - To deploy a new tag/release on production stage : ::

        $ fab tag:1.0.1 prod deploy

    - if something went wrong during deploy process you could rollback previous release : ::

        $ fab prod rollback

    - To deploy with arguments : ::

        $ fab tag:master test --set default_db_host='localhost',default_db_name='mydb',default_db_user='myuser',default_db_password='mypass' deploy

    - Be carefull with --set if you want to pass booleans argument for example verbose_output=False : ::

        $ fab tag:master test --set  verbose_output= deploy

    - See fabric documentation for more infos : http://fabric.readthedocs.org

Tips
----


.. _databases-part:

Databases
~~~~~~~~~

    - django+sqlite3 : if you use sqlite3 with django, don't put your .db file in the same folder as your application. It will be erased for each deployement !

    - Specific oracle installation optional settings for django and bottle applications : ::

        env.oracle_client_version = '11.2'
        env.oracle_download_url = 'http://librepo.net/lib/oracle/'
        env.oracle_remote_dir = 'oracle_client'
        env.oracle_packages = ['instantclient-basic-linux-x86-64-11.2.0.2.0.zip',
                               'instantclient-sdk-linux-x86-64-11.2.0.2.0.zip',
                               'instantclient-sqlplus-linux-x86-64-11.2.0.2.0.zip']


.. _maintenance-mode:

Maintenance mode
~~~~~~~~~~~~~~~~

    - For a django (or bottle) webapp deployement you can set the webserver to be in maintenance mode before deploying. For that purpose you could import in your fabfile pydiploy.django.set_app_up and pydiploy.django.set_app_down in a task :

      .. code-block:: python

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

        $ fab prod set_down

    - When setting the site in maintenance mode you could customize title and text of the maintenance page : ::

        fab prod set_down --set maintenance_title='Webapp is down !',maintenance_text='Time for maintenance, please come back later'

    - If you want to permanently change the default maintenance page you could set env vars in fabfile :

      .. code-block:: python

          # Put this somewhere in the fabfile

          env.maintenance_title='Webapp is down !'
          env.maintenance_text='Time for maintenance, please come back later'

    - Toggle to up mode and deactivate maintenance page : ::

        $ fab prod set_up

Run tasks in parallel
~~~~~~~~~~~~~~~~~~~~~

    - By default pydiploy (via fabric) executes tasks serially : ::

        for example if you have 4 servers :

        $ fab tag:master test deploy

        will run like this :
        deploy on web1
        deploy on web2
        deploy on web3
        deploy on web4

        instead you can use fabric's parallel mode :

        $ fab -P tag:master test deploy    (or set a env.parallel = True in fabfile)

        will run like this :

        deploy on web1,web2,web3,web4

    - Be carefull with parallel mode as env.vars are reseted not all tasks are callable for now !

    - For password prompt use fab -I

    - see also : Fabric documentation http://docs.fabfile.org/en/latest/usage/parallel.html for parallel execution mode

    - see also : Fabric documentation http://docs.fabfile.org/en/latest/usage/fab.html#cmdoption-I for forcing a password prompt at the start of the session

Managing output
~~~~~~~~~~~~~~~

    - By default fabric and so pydiploy is very verbose all levels (ie debug), are on.

    - When using command line you can add --hide=LEVELS or --show=LEVELS parameters.

    - You can disable verbose output on configuration checking by setting env.verbost_ouput=False or in terminal : ::

        $ fab test --set verbose_ouput=

    - You can disable also configuration checking by setting env.no_config_test=True or in terminal : ::

        $ fab test --set no_config_test

    - see also Fabric documentation http://docs.fabfile.org/en/latest/usage/output_controls.html for output levels


Optional parameters
~~~~~~~~~~~~~~~~~~~

    - dest_path specifies a local temp dir if dest_path not set /tmp is used : ::

        env.dest_path = '/home/myuser/deploy/tmp'

    - excluded_files used to specify files that should be excluded when deploying app for files that are not in .gitignore file : ::

        env.excluded_files = ['config.py-DIST','README.rst']

    - extra_ppa_to_install adds extra(s) ppa's sourc(e)s when setting server : ::

        extra_ppa_to_install = ['ppa:vincent-c/ponysay']

    - extra_source_to_install adds extra(s) debian sourc(e)s when setting server : ::

        extra_source_to_install = [['mongodb', 'http://downloads-distro.mongodb.org/repo/ubuntu-upstart', 'dist', '10gen'], ['deb-src', 'http://site.example.com/debian', 'distribution', 'component1', 'component2', 'component3']]   

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

    - maintenance_title and maintenance_text (see `maintenance-mode`_ for more infos) : ::

        env.maintenance_title='Webapp is down !'
        env.maintenance_text='Time for maintenance, please come back later'

    - circus_package_name provides an alternate repository url for specific circus package : ::

        env.circus_package_name = 'https://github.com/githubaccount/circus/archive/master.zip'

    - no_circus_web if sets to True, circus-web package will not be installed during pre_install process : ::

        env.no_circus_web = True

    - nginx_location_extra_directives adds specific directives in location part of nginx config file : ::

        env.nginx_location_extra_directives = ['proxy_read_timeout 120']

    - env.nginx_force_start if True, it forces to start nginx when nginx is not started : ::

        env.nginx_force_start = False

    - oracle_* : see `databases`_ for more infos on required parameters.

    - socket_host used to force a socket host other thant hostname in circus app config file : ::

        env.socket_host = True
