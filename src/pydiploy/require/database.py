"""
Database
========

Requires function to install database client for Python ::

    sqlite3
    oracle
    postgresql
    mysql

"""


from fabtools import require


def sqlite3(use_sudo=False, user=None):
    """
    Require python client for sqlite3

    Installing in a virtualenv ::

        from fabtools.python import virtualenv
        from pydiploy import require

        with virtualenv('/path/to/virtualenv'):
            require.database.sqlite3()

    Installing for wide system ::

        from pydiploy import require

        require.database.sqlite3(use_sudo=True)
    """

    require.deb.package('libsqlite3-dev', update=True)
    require.python.package('pysqlite', upgrade=True, use_sudo=use_sudo,
            user=user)
