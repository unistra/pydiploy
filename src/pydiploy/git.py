"""
Git
===

Create an archive from a remote or directly from a project
"""

import os

from fabric.api import abort
from fabric.api import cd
from fabric.api import lcd
from fabric.api import local
from fabric.api import put
from fabric.api import run
from fabric.api import task


def archive(filename, path='/tmp', format="tar.gz", tag="HEAD", remote="",
        prefix="", project_path="."):
    """
    """
    if format not in ('tar', 'tar.gz', 'zip'):
        abort('Git archive format not supported: %s' % format)

    gzip = format == 'tar.gz'

    if os.path.splitext(filename)[1] != format:
        filename += '.%s' % format

    options = ['--format=%s' % (gzip and 'tar' or format)]
    if remote:
        options.append('--remote=%s' % remote)
    if prefix:
        options.append('--prefix=%s' % prefix)

    command = 'git archive %s %s'
    if gzip:
        command += ' |gzip > %s/%s' % (path, filename)
    else:
        options.append('-o %s/%s' % (path, filename))
    options_build = ' '.join(options)

    if not remote and project_path:
        with lcd(project_path):
            local(command % (options_build, tag))
    else:
        local(command % (options_build, tag))


def push_tag(tag="HEAD", format="tar.gz", remote="", project_path="."):
    """
    """
    project_name = os.path.basename(os.path.abspath(project_path))
    archive_name = '%s-%s' % (project_name, tag)
    prefix = '%s/' % archive_name
    archive(archive_name, tag=tag, prefix=prefix, format=format,
            project_path=project_path, remote=remote)
    with lcd('/tmp'):
        put('%s.%s' % (archive_name, format), '/tmp')
    with cd('/tmp'):
        if format == 'tar.gz':
            run('tar xvf %s.tar.gz' % archive_name)
        else:
            run('unzip %s.zip' % archive_name)
    return '/tmp/%s' % archive_name
