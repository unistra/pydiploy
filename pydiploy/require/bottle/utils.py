# -*- coding: utf-8 -*-
import os
import re
import fabric
import fabtools
from fabric.api import env
from pydiploy.decorators import do_verbose


@do_verbose
def extract_settings():
    """ Extracts settings from django settings files. """

    # get the remote file
    fabric.api.get(env.previous_settings_file, local_path=env.local_tmp_dir)
    settings_file = os.path.join(env.local_tmp_dir, '%s.py' % env.goal)

    # open and read the data from the downloaded file
    with open(settings_file, 'r') as settings_fh:
        settings_data = settings_fh.readlines()

    # search data based on map_settings env attribute for the right goal
    default_pattern = re.compile(r'[ ]*[\'"]{1}(.*)[\'"]{1}')
    for key, to_match in env.map_settings.items():
        if len(to_match) == 2:
            to_match, pattern = to_match[0], re.compile(to_match[1])
        else:
            pattern = default_pattern

        for line in settings_data:
            try:
                settings_key, value = line.split('=', 1)
            except ValueError:
                continue
            if to_match == settings_key.strip():
                setting_value = pattern.match(value.strip())
                if setting_value:
                    setattr(env, key, setting_value.group(1))
                    break


@do_verbose
def app_settings(**kwargs):
    """ Manages django settings file """

    settings_present = fabtools.files.is_file(path=env.previous_settings_file,
                                              use_sudo=True)

    # if values are set within the --set option on command line
    kwargs.update({
        key: value for key, value in env.items() if key in env.map_settings
    })

    if settings_present:
        fabric.api.execute(extract_settings)

    else:
        if "secret_key" in env.map_settings:
            fabric.api.execute(generate_secret_key)

    for map_setting, setting_value in kwargs.items():
        if setting_value:
            setattr(env, map_setting, setting_value)

    fabric.api.require(*env.map_settings.keys())
    settings_dir = os.path.join(env.local_tmp_root_app_package, 'settings')

    fabtools.files.upload_template('%s.py' % env.goal,
                                   env.remote_settings_file,
                                   template_dir=settings_dir,
                                   context=env,
                                   use_sudo=True,
                                   user=env.remote_owner,
                                   mode='644',
                                   chown=True,
                                   use_jinja=True)


@do_verbose
def deploy_environ_file():
    """ Uploads environ.py template on remote """

    fabtools.files.upload_template('environ.py',
                                   os.path.join(
                                       env.remote_base_package_dir,
                                       'environ.py'),
                                   template_dir=env.local_tmp_root_app_package,
                                   context=env,
                                   use_sudo=True,
                                   user=env.remote_owner,
                                   chown=True,
                                   mode='644',
                                   use_jinja=True)


@do_verbose
def deploy_wsgi_file():
    """ Uploads wsgi.py template on remote """

    fabtools.files.upload_template('wsgi.py',
                                   os.path.join(
                                       env.remote_base_package_dir, 'wsgi.py'),
                                   template_dir=env.local_tmp_root_app_package,
                                   context=env,
                                   use_sudo=True,
                                   user=env.remote_owner,
                                   chown=True,
                                   mode='644',
                                   use_jinja=True)
