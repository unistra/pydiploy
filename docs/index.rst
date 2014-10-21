========
pydiploy
========

About
=====

.. include:: ../README.rst

.. _documentation-index:

Documentation
=============

.. _api_doc:

.. toctree::
   api/prepare
   api/params
   api/django
   api/require/django/command
   api/require/django/utils
   api/require/python/utils
   api/require/python/virtualenv
   api/require/databases/databases
   api/require/circus
   api/require/git
   api/require/nginx
   api/require/releases_manager
   api/require/system

Examples
========

.. _examples_doc:

.. toctree::
   examples/fabfiles/fabfile_nginx_circus_django

Templates
=========

Templates are used for major configs files in pydiploy.

.. _templates_doc:

.. toctree::
   :glob:

   templates/*


Dev tools
=========

Sublime text 2/3
----------------

You can use the snippet in the tools folder which can help you to generate a standard fabfile for the library.
Trigger is "pydiployfab"

.. literalinclude:: /../tools/pydiployfabfile.sublime-snippet
   :language: python

.. seealso::

   `Sublime text documentation for snippets <http://docs.sublimetext.info/en/latest/extensibility/snippets.html?highlight=snippet>`_
      Sublime text unofficial documentation.

Vim plugin
----------

.. literalinclude:: /../tools/pydiploy-vim/plugin/pydiployfabfile.vim
   :language: bash

Install this plugin in your ~/.vim/plugin or ~/.vim/bundle directory when editing a file in vim first save the file (type :file fabfile.py for example) and then use the command :PYDIPLOYFAB to generate a standard fabfile.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

