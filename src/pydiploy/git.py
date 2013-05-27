"""
Git
===

Create an archive from a remote or directly from a project
"""


import os

from fabric.api import cd
from fabric.api import put
from fabric.api import run

from .require import git


def deploy(project_name, tag, remote='', destination_directory='/tmp'):
    tag = tag.lower()
    archive_name = '%s-%s' % (project_name, tag)
    archive_path = git.archive(archive_name, tag=tag, remote=remote,
            prefix='%s%s' % (archive_name, os.path.sep))

    put(archive_path, destination_directory)
    with cd(destination_directory):
        run('tar xvf %s.tar.gz' % archive_name)

    return archive_name
