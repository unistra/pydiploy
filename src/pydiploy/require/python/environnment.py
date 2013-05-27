# -*- coding: utf-8 -*-

"""
"""

import os
from fabric.api import env
import fabtools
from pydiploy.system import remote_home


def pypirc(local_name, local_uri, local_user, local_password,
        system_user, system_group):
    """
    """
    home_directory = remote_home(system_user)
    fabtools.require.files.template_file(
            path=os.path.join(home_directory, '.pypirc'),
            template_contents=PYPIRC, context=locals(),
            mode='755', owner=system_user, group=system_group,
            use_sudo=True
    )


PYPIRC = """\
[distutils]
index-servers = 
    pypi
    %(local_name)s

[pypi]
repository: https://pypi.python.org/simple/

[%(local_name)s]
repository: %(local_uri)s
username: %(local_user)s
password: %(local_password)s
"""
