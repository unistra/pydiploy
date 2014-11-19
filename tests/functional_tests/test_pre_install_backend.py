import pytest
from fabric.api import run, env
import pydiploy
import os


pytestmark = pytest.mark.network


def buildmyenv():
    env.user = 'vagrant'  # user for ssh

    env.remote_owner = 'django'  # remote server user
    env.remote_group = 'di'  # remote server group

    env.application_name = 'myapp'   # name of webapp
    env.root_package_name = 'myapp'  # name of app in webapp

    env.remote_home = '/home/django'  # remote home root
    env.remote_python_version = 3.4  # python version
    env.remote_virtualenv_root = os.path.join(env.remote_home, '.virtualenvs')  # venv root
    env.remote_virtualenv_dir = os.path.join(env.remote_virtualenv_root,
                                     env.application_name)  # venv for webapp dir
    env.remote_repo_url = 'git@git.net:myapp.git'  # git repository url
    env.local_tmp_dir = '/tmp'  # tmp dir
    env.remote_static_root = '/var/www/static'  # root of static files
    env.locale = 'fr_FR.UTF-8'  # locale to use on remote
    env.timezone = 'Europe/Paris'  # timezone for remote
    env.keep_releases = 2  # number of old releases to keep before cleaning

    env.circus_package_name = 'https://github.com/morganbohn/circus/archive/master.zip'
    env.tag = 'master'

    env.roledefs = {
        'web': ['127.0.0.1'],
        'lb': ['127.0.0.1'],
    }
    env.backends = env.roledefs['web']
    env.server_name = 'myapp-dev.net'
    env.short_server_name = 'myapp-dev'
    env.static_folder = '/site_media/'
    env.server_ip = '127.0.0.1'
    env.no_shared_sessions = False
    env.server_ssl_on = False
    env.goal = 'dev'
    env.socket_port = '8001'
    env.map_settings = {
        #'ldap_user': "DATABASES['ldap']['USER']",
        #'ldap_password': "DATABASES['ldap']['PASSWORD']"
    }

    pydiploy.prepare.build_env()


@pytest.fixture(scope='module', autouse=True)
def pre_install():
    buildmyenv()
    pydiploy.django.pre_install_backend()


def test_user_created(pre_install):
    django = run('getent passwd %s' % env.remote_owner)
    assert django == '%s:x:1001:1003::/home/%s:/bin/bash' % (env.remote_owner,
                                                             env.remote_owner)

    django = run('getent group %s' % env.remote_group)
    assert django == '%s:x:1003:' % env.remote_group


def test_locale(pre_install):
    lang = run('cat /etc/default/locale |grep LANG=')
    assert lang == 'LANG=%s' % env.locale


def test_timezone(pre_install):
    lang = run("cd /usr/share/zoneinfo && find * -type f -exec sh -c \"diff -q /etc/localtime '{}' > /dev/null && echo {}\" \;")
    assert lang == env.timezone


def test_app_packages(pre_install):
    install = run("dpkg-query -W -f='${Status}' gettext")
    assert install == 'install ok installed'
    install = run("pip freeze |grep python-ldap |cut -d '=' -f1")
    assert install == 'python-ldap'
    install = run("dpkg-query -W -f='${Status}' libpq-dev")
    assert install == 'install ok installed'
    install = run("dpkg-query -W -f='${Status}' python-dev")
    assert install == 'install ok installed'
    install = run("dpkg-query -W -f='${Status}' python-pip")
    assert install == 'install ok installed'
    install = run("dpkg-query -W -f='${Status}' python%s-dev" % env.remote_python_version)
    assert install == 'install ok installed'


def test_circus(pre_install):
    install = run("pip freeze |grep circus |cut -d '=' -f1")
    assert install == 'circus\r\ncircus-web'

    circusconf = run('[ -e %s/.circus.d ] && echo "Found" || echo "Not found"' % env.remote_home)
    assert circusconf == "Found"
    circusconf = run('[ -e %s/.circus.ini ] && echo "Found" || echo "Not found"' % env.remote_home)
    assert circusconf == "Found"

    start = run("status circus |cut -d '/' -f1")
    assert start == "circus stop"


def test_virtualenv(pre_install):
    right_lib = run('[ -e %s/.virtualenvs/%s/lib/python%s ] && echo "Found" || echo "Not found"' % (env.remote_home, env.application_name, env.remote_python_version))
    assert right_lib == "Found"
