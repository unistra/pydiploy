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
    - Use following command to install/deploy an application in production stage : ::

        fab tag:master prod pre_install deploy post_install
    - To deploy a new tag/release on production stage : ::

        fab tag:1.0.1 prod deploy
    - if something went wrong during deploy process you could rollback previous release : ::

        fab tag:master prod rollback
    - To deploy with arguments : ::

        fab tag:master test --set default_db_host='localhost',default_db_name='mydb',default_db_user='myuser',default_db_password='mypass' deploy

    - See fabric documentation for more infos : http://fabric.readthedocs.org

Tips
----

    - django+sqlite3 : if you use sqlite3 with django, don't put your .db file in the same folder as your application. It will be erased for each deployement !

