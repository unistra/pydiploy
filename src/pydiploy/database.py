"""
"""

from pydiploy import require as dip_require


def install(engines=None):
    if engines is None:
        engines = dip_require.django.db_engines()
    for engine in engines:
        try:
            install_func = getattr(dip_require.database, engine)
        except:
            pass
        else:
            install_func()
