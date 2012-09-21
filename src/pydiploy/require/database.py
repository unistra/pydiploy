"""
Database
"""

from fabric import env

from fabtools import require


def sqlite3():
    """
    """
    require.deb.package('libsqlite3-dev', update=True)
    with require.python.virtualenv(env.virtualenv_dir):
        require.python.package('pysqlite', upgrade=True)
