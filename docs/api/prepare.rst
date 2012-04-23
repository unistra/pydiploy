=========================
Préparation de la machine
=========================

.. automodule:: pydiploy.prepare


API publique 
============
Toutes les fonctions listées ici sont accessibles via les tâches Fabric et peuvent être utilisées dans des tâches
Fabric plus globales.


.. automethod:: pydiploy.prepare.install_tools

.. automethod:: pydiploy.prepare.create_python_env

.. automethod:: pydiploy.prepare.update_python_env

.. automethod:: pydiploy.prepare.oracle_client

.. automethod:: pydiploy.prepare.sap_client


API privée
==========
Ces fonctions peuvent être  utilisées pour créer de nouvelles tâches Fabric personnalisées

.. automethod:: pydiploy.prepare.setuptools

.. automethod:: pydiploy.prepare.virtualenv

.. automethod:: pydiploy.prepare.update_bashrc

.. automethod:: pydiploy.prepare.generate_bash_profile
