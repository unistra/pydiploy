# -*- coding: utf-8 -*-

import os
import fabtools
from time import time
from fabric.api import sudo, execute, env, require, lcd, local, basename
from fabric.contrib.project import rsync_project
from .system import permissions, symlink
from .git import archive


def set_current():
    """Use current directory for new release"""
    sudo("ln -nfs %(current_release)s %(current_path)s"
         % {'current_release': env.remote_current_release,
            'current_path': env.remote_current_path})


def setup():
    """Config stuff for deployement"""
    sudo("mkdir -p %(remote_domain_path)s/{releases,shared}" %
         {'remote_domain_path': env.remote_project_dir})
    sudo("mkdir -p %(remote_shared_path)s/{config,log}" %
         {'remote_shared_path': env.remote_shared_path})
    execute(permissions)


def cleanup():
    """Tidy up old stuff on remote server"""
    if len(env.releases) >= env.keep_releases:
        directories = env.releases
        directories.reverse()
        del directories[:env.keep_releases]
        env.directories = ' '.join(["%(releases_path)s/%(release)s" %
                                   {'releases_path': env.remote_releases_path,
                                    'release': release} for release in directories])

        sudo("rm -rf %(directories)s" % {'directories': env.directories})


def deploy_code():
    require('tag', provided_by=['tag', 'head'])
    require('remote_project_dir', provided_by=['test', 'prod'])
    tarball = archive(env.application_name,
                      prefix='%s-%s/' % (env.application_name,
                                         env.tag.lower()),
                      tag=env.tag,
                      remote=env.remote_repo_url)
    with lcd('/tmp'):
        local('tar xvf %s' % basename(tarball))

    exclude_files = ['fabfile', 'MANIFEST.in', '*.ignore', 'docs', 'data',
                     'log', 'bin', 'manage.py', 'cmscts/wsgi.py', '*.db',
                     '.gitignore']
    exclude_files += ['%s/settings/%s.py' % (env.root_package_name, goal)
                      for goal in ('dev', 'test', 'prod')]

    env.remote_current_release = "%(releases_path)s/%(time).0f" % {
        'releases_path': env.remote_releases_path, 'time': time()}

    rsync_project(env.remote_current_release,
                  '/tmp/%s-%s/' % (env.application_name, env.tag.lower()),
                  delete=True,
                  extra_opts='--rsync-path="sudo -u %s rsync"' % env.remote_owner,
                  exclude=exclude_files)

    sudo(
        'chown -R %(user)s:%(group)s %(project_dir)s' % {'user': env.remote_owner,
                                                         'group': env.remote_group,
                                                         'project_dir': env.remote_current_release})
    # symlink with new release
    execute(symlink)
    # set current directory with new release
    execute(set_current)

    # uploading manage.py template
    fabtools.files.upload_template('manage.py',
                                   os.path.join(
                                       env.remote_current_release, 'manage.py'),
                                   template_dir=env.local_tmp_root_app,
                                   context=env,
                                   use_sudo=True,
                                   user=env.remote_owner,
                                   chown=True,
                                   mode='744',
                                   use_jinja=True)

    # uploading wsgi.py template
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
    local('rm %s' % tarball)


def rollback_code():
    """Rolls back to the previously deployed version"""
    if len(env.releases) >= 2:
        env.current_release = env.releases[-1]
        env.previous_revision = env.releases[-2]
        env.current_release = "%(releases_path)s/%(current_revision)s" % \
            {'releases_path': env.remote_releases_path,
             'current_revision': env.current_revision}
        env.remote_previous_release = "%(releases_path)s/%(previous_revision)s" % \
            {'releases_path': env.remote_releases_path,
             'previous_revision': env.previous_revision}
        sudo("rm %(current_path)s; ln -s %(previous_release)s %(current_path)s && rm -rf %(current_release)s" %
             {'current_release': env.current_release, 'previous_release': env.previous_release, 'current_path': env.remote_current_path})
