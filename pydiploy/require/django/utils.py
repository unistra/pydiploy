# -*- coding: utf-8 -*-

import random
import string
import os
import re
from fabric.api import env
import fabtools
import fabric


def generate_secret_key():
    """
    Generates the django's secret key
    """

    letters = string.ascii_letters + string.punctuation.replace('\'', '')
    random_letters = map(lambda i: random.SystemRandom().choice(letters),
                         range(50))

    env.secret_key = ''.join(random_letters)


def extract_settings():
    """
    Extracts settings from django settings files
    """

    print('in')
    # get the remote file
    fabric.api.get(env.remote_settings_file, local_path=env.local_tmp_dir)

    # open and read the data from the downloaded file
    with open(os.path.join(env.local_tmp_dir, '%s.py' % env.goal), 'r') as settings_fh:
        settings_data = settings_fh.readlines()

    # search data based on map_settings env attribute for the right goal
    for key, pattern in env.map_settings.items():
        for line in settings_data:
            real_pattern = pattern.replace('[', '\[').replace(']', '\]')
            setting = re.match(r'%s[ ]*=[ ]*[\'"](.*)[\'"]' % real_pattern,
                               line.strip())
            if setting:
                setattr(env, key, setting.group(1))
                break


def app_settings(**kwargs):
    """
    Manages django settings file
    """
    settings_present = fabtools.files.is_file(path=env.remote_settings_file,
                                              use_sudo=True)

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
