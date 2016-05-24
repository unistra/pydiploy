# -*- coding: utf-8 -*-

"""  This module builds env. vars used for the whole library, and check them methods are :

* _get_current_role() : gets role used in fabric
* build_env : inits all env. vars used by the library
* check_req_pydiploy_version : checks required version of pydiploy for a specific fabfile
* init_params : gets required and optional parameters used for config checker
* tag : gets the tag used to deploy the app
* test_config : checks configuration in fabfile


"""

import os

import fabric
import fabtools
from fabric.api import env
from pkg_resources import Requirement, resource_filename
from pydiploy.params import PARAMS
from pydiploy.require.git import check_tag_exist
from pydiploy.version import __version__, __version_info__


@fabric.api.task
def tag(version):
    """ Defines tag to deploy """

    if "pydiploy_version" in env:
        fabric.api.abort(fabric.colors.red(
            "tag should be set before calling goal (ex: fab tag:master test deploy)"))
    if check_tag_exist(version):
        env.tag = version
    else:
        fabric.api.abort(fabric.colors.red(
            "tag/branch provided is not in the repository please fix this first"))


def init_params(application_type='default'):
    """ Sets required params and its description """

    try:
        required_params, optional_params = PARAMS[application_type]['required_params'], PARAMS[application_type]['optional_params']
    except KeyError:
        fabric.api.abort(fabric.colors.red(
            "application_type '%s' doesn't exists" % application_type))
    return required_params, optional_params


def build_env():
    """ Builds env vars """

    env.pydiploy_version = __version__

    # check pydiploy version required by fabfile (major version number)
    if "req_pydiploy_version" in env:
        if not check_req_pydiploy_version():
            if not fabric.contrib.console.confirm(
                    "\nYour fabfile require pydiploy %s and pydiploy %s is installed ! \
                    \nBe sure that your fabfile complies last pydiploy evolutions. \
                    \nContinue at your own risks ! \
                    \n\nDo you want to continue?" %
                    (fabric.colors.red(env.req_pydiploy_version),
                        fabric.colors.red(__version__)), default=False):
                fabric.api.abort("Aborting at user request.")

    # remote home cannot be empty or / path
    if not 'remote_home' in env or not env.remote_home or env.remote_home == "/":
        fabric.api.abort("The remote home cannot be empty or /.")

    # defines destination path for fetched file(s)
    if "dest_path" not in env:
        env.dest_path = env.local_tmp_dir

    if "server_name" in env:
        env.remote_project_dir = os.path.join(env.remote_home, env.server_name)
    else:
        env.remote_project_dir = os.path.join(env.remote_home, env.application_name)

    if "tag" in env:
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

    # populate env vars for current release / n-1 release
    if not "releases" in env:
        fabric.api.execute(process_releases)

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

    if 'application_type' in env:
        application_type = env.application_type
    else:
        application_type = 'default'

    if not test_config(verbose=verbose_value, application_type=application_type):
        if not fabric.contrib.console.confirm("Configuration test %s! Do you want to continue?" % fabric.colors.red('failed'), default=False):
            fabric.api.abort("Aborting at user request.")


@fabric.api.task
def test_config(verbose=True, application_type='default'):
    """ Checks fabfile for required params and optional params """

    if "no_config_test" in env:
        if env.no_config_test:
            return True

    err = []
    req_parameters = []
    opt_parameters = []
    req_params, opt_params = init_params(application_type)
    max_req_param_length = max(map(len, req_params.keys()))
    max_req_desc_length = max(map(len, req_params.values()))
    max_opt_param_length = max(map(len, opt_params.keys()))
    max_opt_desc_length = max(map(len, opt_params.values()))
    current_role = _get_current_role()

    fabric.api.puts("\n\nConfiguration checking for role : %s, host : %s" % (
        fabric.colors.green(current_role), fabric.colors.green(env.host)))
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
            if param == 'dest_path' and env.dest_path == env.local_tmp_dir:
                continue
            opt_parameters.append((param, env[param], desc))

    if err:
        err_nb = len(err)
        if err_nb == len(req_params):
            fabric.api.puts(
                'You need to configure correctly the fabfile please RTFM first !')
        else:
            fabric.api.puts('Config test failed (%s error%s) for role %s:' %
                            (err_nb, 's' if err_nb > 1 else '', current_role))
            fabric.api.puts('%s\n\n* %s\n' % ('-' * 30, '\n* '.join(err)))
            fabric.api.puts(
                'Please fix them or continue with possible errors.')
        return False
    elif verbose:
        fabric.api.puts('\n\nRequired parameters list : \n\n')
        for param, value, description in req_parameters:
            fabric.api.puts('* %s %s' %
                            (param.ljust(max_req_param_length), fabric.colors.green(value)))
        fabric.api.puts('\n\nOptional parameters list : \n\n')
        if len(opt_parameters):
            for param, value, description in opt_parameters:
                value = fabric.colors.red("Warning initialized but not set") if not bool(
                    str(value)) ^ bool(value == None) else fabric.colors.green(value)
                fabric.api.puts('* %s %s' %
                                (param.ljust(max_opt_param_length), value))
        else:
            fabric.api.puts("No optional parameter found")
    fabric.api.puts('\n\nRole : %s -> configuration %s!\n\n' %
                    (fabric.colors.green(current_role), fabric.colors.green("OK")))
    return True


def _get_current_role():
    """ Gets fabric current role should be env.effective_roles in future's fabric release """

    try:
        current_role = "Not set!"
        for role in env.roledefs.keys():
            if env.host_string in env.roledefs[role]:
                current_role = role
    finally:
        return current_role


def check_req_pydiploy_version():
    """ Checks pydiploy version required with pydiploy version installed """

    if "req_pydiploy_version" in env:
        major_version_installed = __version_info__[0:2]
        major_version_required = tuple(
            [int(num) for num in env.req_pydiploy_version.split('.')])
        if (major_version_installed != major_version_required[0:2]):
            return False
        return True


def generate_fabfile():
    """ Returns current django_fabfile example """

    fab_sample = resource_filename("pydiploy", "examples/django_fabfile.py")

    with open(fab_sample) as f:
        return f.read()


def generate_fabfile_simple():

    fab_sample_simple = resource_filename("pydiploy", "examples/simple_fabfile.py")

    with open(fab_sample_simple) as f:
        return f.read()


def generate_fabfile_bottle():

    fab_sample_bottle = resource_filename("pydiploy", "examples/bottle_fabfile.py")

    with open(fab_sample_bottle) as f:
        return f.read()


def process_releases():
    """ Populates env vars for releases (current, old...) """
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
