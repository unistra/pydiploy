# -*- coding: utf-8 -*-

"""  This module builds env. vars used for the whole library methods are :

* tag : get the tag used to deploy the app
* build_env : inits all env. vars used by the library

"""

import os
import fabric
import fabtools

from fabric.api import env


@fabric.api.task
def tag(version):
    """ Defines tag to deploy """

    env.tag = version


def init_required_params():
    """ sets required params and its description """

    # TODO use more descriptives values !!!!!
    required_params = {'user': "user for ssh",
                       'remote_owner': "remote server user",
                       'remote_group': "remote server user group",
                       'application_name': "name of wepapp",
                       'root_package_name': "name of app in webapp",
                       'remote_home': "remote home root",
                       'remote_python_version': "remote python version to use",
                       'remote_virtualenv_root': "remote virtualenv root",
                       'remote_virtualenv_dir': "remote virtualenv dir for wepapp",
                       'remote_repo_url': "git repository url",
                       'local_tmp_dir': "local tmp dir",
                       'remote_static_root': "root of static files",
                       'locale': "locale to use on remote",
                       'timezone': "timezone used on remote",
                       'keep_releases': "number of old releases to keep",
                       'roledefs': "Role to use to deploy",
                       'backends': "backend to use to deploy",
                       'server_name': "name of webserver",
                       'short_server_name': "short name of webserver",
                       'static_folder': "path of static folder",
                       'goal': "stage to use to deploy (dev,prod,test...)",
                       'socket_port': "port to use for socket",
                       'socket_host': "socket host"}
    return required_params


def build_env():
    """
    Builds env vars
    """

    # checks if tag is specified if not fabric.api.prompt user
    if "tag" not in env:
        env.tag = fabric.api.prompt('Please specify target tag used: ')

    # defines destination path for fetched file(s)
    if "dest_path" not in env:
        env.dest_path = env.local_tmp_dir

    env.remote_project_dir = os.path.join(env.remote_home, env.server_name)
    env.local_tmp_root_app = os.path.join(env.local_tmp_dir,
                                          '%(application_name)s-%(tag)s' % env)
    env.local_tmp_root_app_package = os.path.join(env.local_tmp_root_app,
                                                  env.root_package_name)

    env.remote_current_path = os.path.join(env.remote_project_dir, 'current')
    env.remote_releases_path = os.path.join(env.remote_project_dir, 'releases')
    env.remote_shared_path = os.path.join(env.remote_project_dir, 'shared')
    env.remote_base_package_dir = os.path.join(env.remote_current_path,
                                               env.root_package_name)
    env.remote_settings_dir = os.path.join(
        env.remote_base_package_dir, 'settings')
    env.remote_settings_file = os.path.join(env.remote_settings_dir,
                                            '%s.py' % env.goal)

    env.lib_path = os.path.dirname(__file__)

    if not "releases" in env:
        if fabtools.files.is_dir(env.remote_releases_path):
            env.releases = sorted(fabric.api.run('ls -x %(releases_path)s' %
                                                 {'releases_path': env.remote_releases_path}).split())
            env.previous_settings_file = ""

            if len(env.releases) >= 1:
                env.current_revision = env.releases[-1]
                env.current_release = "%(releases_path)s/%(current_revision)s" % \
                                      {'releases_path': env.remote_releases_path,
                                       'current_revision': env.current_revision}
                # warning previous settings file before deployement !!!!!
                env.previous_release_base_package_dir = os.path.join(
                    env.current_release, env.root_package_name)
                env.previous_release_settings_dir = os.path.join(
                    env.previous_release_base_package_dir, 'settings')
                env.previous_settings_file = os.path.join(
                    env.previous_release_settings_dir, '%s.py' % env.goal)

            if len(env.releases) > 1:
                env.previous_revision = env.releases[-2]
                env.previous_release = "%(releases_path)s/%(previous_revision)s" % \
                                       {'releases_path': env.remote_releases_path,
                                        'previous_revision': env.previous_revision}

    # define main goals
    env.goals = ['dev', 'test', 'prod']

    # if set in fabfile add extra goals
    if "extra_goals" in env:
        env.goals += env.extra_goals

    if not test_config():
        if not fabric.contrib.console.confirm("Configuration test %s! Do you want to continue?" % fabric.colors.red('failed'), default=False):
            fabric.api.abort("Aborting at user request.")


@fabric.api.task
def test_config(verbose=True):
    err = []
    parameters = []
    returned_params = init_required_params()
    max_param_length = max(map(len, returned_params.keys()))
    max_desc_length = max(map(len, returned_params.values()))

    for param, desc in returned_params.items():
        if param not in env or not env[param]:
            err.append("%s -> %s : missing" %
                       (param.ljust(max_param_length), desc.ljust(max_desc_length)))
        elif verbose:
            parameters.append((param, env[param], desc))

    if err:
        err_nb = len(err)
        if err_nb == len(returned_params):
            fabric.api.puts(
                'You need to configure correctly the fabfile please RTFM first !')
        else:
            fabric.api.puts('Config test failed (%s error%s) :' %
                            (err_nb, 's' if err_nb > 1 else ''))
            fabric.api.puts('%s\n\n* %s\n' % ('-' * 30, '\n* '.join(err)))
            fabric.api.puts(
                'Please fix them or continue with possible errors.')
        return False
    elif verbose:
        for param, value, description in parameters:
            fabric.api.puts('* %s %s' %
                            (param.ljust(max_param_length), fabric.colors.green(value)))

    fabric.api.puts('\n\nConfiguration OK!\n\n')
    return True
