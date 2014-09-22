# -*- coding: utf-8 -*-

"""  This module builds env. vars used for the whole library methods are :

* tag : get the tag used to deploy the app
* build_env : inits all env. vars used by the library

"""

import os

import fabric
import fabtools
from fabric.api import env

from pydiploy.params import PARAMS


@fabric.api.task
def tag(version):
    """ Defines tag to deploy """

    env.tag = version


def init_params():
    """ sets required params and its description """

    return PARAMS['default']['required_params'], PARAMS['default']['optional_params']


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

    if "previous_settings_file" not in env:
        env.previous_settings_file = ""

    if "socket_host" not in env:
        env.socket_host = env.host

    if not "releases" in env:
        if fabtools.files.is_dir(env.remote_releases_path):
            env.releases = sorted(fabric.api.run('ls -x %(releases_path)s' %
                                                 {'releases_path': env.remote_releases_path}).split())

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

    # verbose display
    if "verbose_output" in env:
        verbose_value = env.verbose_output
    else:
        verbose_value = True

    if not test_config(verbose=verbose_value):
        if not fabric.contrib.console.confirm("Configuration test %s! Do you want to continue?" % fabric.colors.red('failed'), default=False):
            fabric.api.abort("Aborting at user request.")


@fabric.api.task
def test_config(verbose=True):
    err = []
    req_parameters = []
    opt_parameters = []
    req_params, opt_params = init_params()
    max_req_param_length = max(map(len, req_params.keys()))
    max_req_desc_length = max(map(len, req_params.values()))
    max_opt_param_length = max(map(len, opt_params.keys()))
    max_opt_desc_length = max(map(len, opt_params.values()))

    for param, desc in sorted(req_params.items()):
        if param not in env:
            err.append("%s -> %s : missing" %
                       (param.ljust(max_req_param_length), desc.ljust(max_req_desc_length)))
        elif not bool(env[param]):
            err.append("%s -> %s : not set" %
                       (param.ljust(max_req_param_length), desc.ljust(max_req_desc_length)))
        elif verbose:
            req_parameters.append((param, env[param], desc))

    for param, desc in sorted(opt_params.items()):
        if param in env and verbose:
            if param == 'socket_host' and env.socket_host == env.host:
                continue
            elif param == 'dest_path' and env.dest_path == env.local_tmp_dir:
                continue
            opt_parameters.append((param, env[param], desc))

    if err:
        err_nb = len(err)
        if err_nb == len(req_params):
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
        fabric.api.puts('Required parameters list : \n\n')
        for param, value, description in req_parameters:
            fabric.api.puts('* %s %s' %
                            (param.ljust(max_req_param_length), fabric.colors.green(value)))
        fabric.api.puts('\n\nOptional parameters list : \n\n')
        if len(opt_parameters):
            for param, value, description in opt_parameters:
                value = "Warning initialized but not set" if not bool(
                    value) else value
                fabric.api.puts('* %s %s' %
                                (param.ljust(max_opt_param_length), fabric.colors.green(value)))
        else:
            fabric.api.puts("No optionnal parameter found")
    fabric.api.puts('\n\nConfiguration OK!\n\n')
    return True
