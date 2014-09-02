# -*- coding: utf-8 -*-

""" Utilities for django settings. """

import random
import string
import os
import re
from fabric.api import env
import fabtools
import fabric


def generate_secret_key():
    """ Generate the django's secret key. """
    letters = string.ascii_letters + string.punctuation.replace('\'', '')
    random_letters = map(lambda i: random.SystemRandom().choice(letters),
                         range(50))

    env.secret_key = ''.join(random_letters)


def extract_settings():
    """ Extract settings from django settings files. """
    # get the remote file
    fabric.api.get(env.remote_settings_file, local_path=env.local_tmp_dir)
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
                settings_key, value = line.split('=')
            except ValueError:
                continue
            if to_match == settings_key.strip():
                setting_value = pattern.match(value.strip())
                if setting_value:
                    setattr(env, key, setting_value.group(1))
                    break


def app_settings(**kwargs):
    """ Manage django settings file """
    settings_present = fabtools.files.is_file(path=env.remote_settings_file,
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
