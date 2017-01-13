# -*- coding: utf-8 -*-

import os
from time import time

import fabric
import fabtools
import pydiploy
from fabric.api import env
from pydiploy.decorators import do_verbose


@do_verbose
def set_current():
    """
    Uses current directory for new release
    """
    fabric.api.sudo("ln -nfs %(current_release)s %(current_path)s"
                    % {'current_release': env.remote_current_release,
                       'current_path': env.remote_current_path})


@do_verbose
def setup():
    """
    Configs stuff for deployement
    """
    fabric.api.sudo("mkdir -p %(remote_domain_path)s/{releases,shared}" %
                    {'remote_domain_path': env.remote_project_dir})
    fabric.api.sudo("mkdir -p %(remote_shared_path)s/{config,log}" %
                    {'remote_shared_path': env.remote_shared_path})
    # extra symlinks if present in settings
    if env.has_key('extra_symlink_dirs'):
        for extra_symlink_dir in env.extra_symlink_dirs:
            fabric.api.sudo("mkdir -p %(remote_shared_path)s/%(shared_dir)s" %
                            {'remote_shared_path': env.remote_shared_path,
                             'shared_dir': os.path.basename(extra_symlink_dir)})

    fabric.api.execute(pydiploy.require.system.permissions)


@do_verbose
def cleanup():
    """
    Cleans old stuff on remote server
    """
    fabric.api.execute(pydiploy.prepare.process_releases)
    if 'releases' in env and len(env.releases) >= env.keep_releases:
        directories = env.releases
        directories.reverse()
        del directories[:env.keep_releases]
        env.directories = ' '.join(["%(releases_path)s/%(release)s" %
                                    {'releases_path': env.remote_releases_path,
                                     'release': release} for release in directories])

        fabric.api.sudo("rm -rf %(directories)s" %
                        {'directories': env.directories})


@do_verbose
def deploy_code():
    """
    Deploys code according to tag in env var
    """

    # checks if tag is specified if not fabric.api.prompt user
    if "tag" not in env:
        tag_requested = fabric.api.prompt('Please specify target tag used: ')
        while(not pydiploy.require.git.check_tag_exist(tag_requested)):
            tag_requested = fabric.api.prompt(
                'tag %s unknown please specify valid target tag used: ' % fabric.colors.red(tag_requested))

        env.tag = tag_requested

    env.local_tmp_root_app = os.path.join(env.local_tmp_dir,
                                          '%(application_name)s-%(tag)s' % env)
    env.local_tmp_root_app_package = os.path.join(env.local_tmp_root_app,
                                                  env.root_package_name)

    fabric.api.require('tag', provided_by=['tag', 'head'])
    fabric.api.require('remote_project_dir', provided_by=env.goals)

    archive_prefix = '%s-%s' % (env.application_name, env.tag.lower())

    tarball = pydiploy.require.git.archive(env.application_name,
                                           prefix='%s/' % archive_prefix,
                                           specific_folder=env.remote_repo_specific_folder if "remote_repo_specific_folder" in env else "",
                                           tag=env.tag,
                                           remote=env.remote_repo_url)

    with fabric.api.lcd(env.local_tmp_dir):
        # remove existing extracted dir from tarball
        if os.path.exists('%s/%s' % (env.local_tmp_dir,archive_prefix)):
            fabric.api.local('rm -rf %s' % archive_prefix)
        fabric.api.local('tar xvf %s' % os.path.basename(tarball))

    if 'run_tests_command' in env and env.run_tests_command:
        run_tests()

    # TODO: see if some excluded files / dir
    # are not in fact usefull in certain projects
    exclude_files = ['fabfile', 'MANIFEST.in', '*.ignore', 'docs',
                     '*.log', 'bin', 'manage.py', '.tox',
                     '%s/wsgi.py' % env.root_package_name, '*.db',
                     '.gitignore', '.gitattributes']
    exclude_files += ['%s/settings/%s.py' % (env.root_package_name, goal)
                      for goal in env.goals]

    if env.has_key('excluded_files'):
        exclude_files += env.excluded_files
    if env.has_key('cfg_shared_files'):
        for cfg_shared_file in env.cfg_shared_files:
            cfg_present = fabtools.files.is_file(
                path='%s/config/%s' % (
                    env.remote_shared_path, os.path.basename(cfg_shared_file)),
                use_sudo=True)
            if cfg_present is None:
                fabtools.files.upload_template('%s/%s/%s' % (
                                               env.local_tmp_dir,
                                               archive_prefix,
                                               cfg_shared_file
                                               ),
                                               os.path.join(
                                               env.remote_shared_path, 'config'),
                                               use_sudo=True)

            exclude_files += [cfg_shared_file]

    if env.has_key('extra_symlink_dirs'):
        for symlink_dir in env.extra_symlink_dirs:
            exclude_files += [symlink_dir]

    env.remote_current_release = "%(releases_path)s/%(time).0f" % {
        'releases_path': env.remote_releases_path, 'time': time()}

    fabric.contrib.project.rsync_project(env.remote_current_release,
                                         '%s/%s/' % (
                                             env.local_tmp_dir,
                                             archive_prefix),
                                         delete=True,
                                         extra_opts='--links --rsync-path="sudo -u %s rsync"' % env.remote_owner,
                                         exclude=exclude_files)

    fabric.api.sudo(
        'chown -R %(user)s:%(group)s %(project_dir)s' % {'user': env.remote_owner,
                                                         'group': env.remote_group,
                                                         'project_dir': env.remote_current_release})
    # symlink with new release
    fabric.api.execute(symlink)
    # set current directory with new release
    fabric.api.execute(set_current)

    # remove git local git archive tarball
    with fabric.api.lcd(env.local_tmp_dir):
        fabric.api.local('rm %s' % os.path.basename(tarball))


@do_verbose
def rollback_code():
    """
    Rolls back to the previously deployed version
    """

    fabric.api.execute(pydiploy.prepare.process_releases)
    if "releases" in env:
        nb_releases = len(env.releases)
        if nb_releases >= 2:
            fabric.api.sudo("rm %(current_path)s; ln -s %(previous_release)s %(current_path)s && rm -rf %(current_release)s" %
                            {'current_release': env.current_release, 'previous_release': env.previous_release, 'current_path': env.remote_current_path})
        # elif nb_releases == 1:
        elif nb_releases == 1:

            fabric.api.puts(fabric.colors.red(
                            'No rollback only one release found on remote !'))
        else:
            fabric.api.sudo("rm %(current_path)s && rm -rf %(previous_release)s" %
                            {'current_path': env.remote_current_path, 'previous_release': env.remote_current_release})


@do_verbose
def symlink():
    """
    Updates symlink stuff to the current deployed version
    """

    # TODO : really usefull ? (eg : for php apps ...)
    fabric.api.sudo("ln -nfs %(shared_path)s/log %(current_release)s/log" %
                    {'shared_path': env.remote_shared_path,
                     'current_release': env.remote_current_release})

    if env.has_key('cfg_shared_files'):
        for cfg_shared_file in env.cfg_shared_files:
            fabric.api.sudo("ln -nfs %(shared_path)s/config/%(file_name)s %(current_release)s/%(file)s" %
                            {'shared_path': env.remote_shared_path,
                             'current_release': env.remote_current_release,
                             'file': cfg_shared_file,
                             'file_name':  os.path.basename(cfg_shared_file)})

    if env.has_key('extra_symlink_dirs'):
        for extra_symlink_dir in env.extra_symlink_dirs:
            fabric.api.sudo("ln -nfs %(shared_path)s/%(dir_name)s %(current_release)s/%(dir_name)s" %
                            {'shared_path': env.remote_shared_path,
                             'current_release': env.remote_current_release,
                             'dir_name':  extra_symlink_dir})

@do_verbose
def run_tests():
    # Runs local unit test
    authorized_commands = ['tox']
    if env.run_tests_command in authorized_commands:
        with fabric.api.lcd('%s/%s-%s/' % (env.local_tmp_dir, env.application_name, env.tag.lower())):
            fabric.api.local(env.run_tests_command)
    else:
        fabric.api.abort(fabric.colors.red("wrong test command. Currently, only tox is supported"))
