# -*- coding: utf-8 -*-
from functools import wraps

import fabric
from fabric.api import env

"""

Decorators

"""


def do_verbose(view_func):
    """
    Print verbose
    """

    @wraps(view_func)
    def wrapper(*args, **kwargs):
        custom_hide = ['running', 'stdout', 'stderr'] if 'verbose_output' in\
            env and not env.verbose_output else []
        with fabric.context_managers.hide(*custom_hide):
            fabric.api.puts("%s : %s" % (view_func.__name__, fabric.colors.green("Executing")))
            res = view_func(*args, **kwargs)
            fabric.api.puts("%s : %s" % (view_func.__name__, fabric.colors.green("Done")))
            return res
    return wrapper
