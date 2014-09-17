import pytest

from fabric.api import quiet, run, shell_env, env

from fabtools.files import is_link
from fabtools.system import distrib_family, set_hostname

import pydiploy
import fabric


pytestmark = pytest.mark.network

env.remote_owner = 'django'  # remote server user
env.remote_group = 'di'  # remote server group

@pytest.fixture(scope='module', autouse=True)
def user():
    fabric.api.execute(pydiploy.require.system.django_user, commands='/usr/bin/rsync')


def test_user_created(user):
    django = run('getent passwd django')
    assert django == 'django:x:1001:1003::/home/django:/bin/bash'
