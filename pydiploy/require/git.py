# -*- coding: utf-8 -*-

"""
Git
===

Create an archive from a remote or directly from a project
"""

import fabric
import os


def archive(filename, path='/tmp', format="tar.gz", tag="HEAD", remote="",
            prefix="", project_path="."):
    """ Creates an archive from a git repository

    * Using at the root path of a local cloned repository. This will create
      a tar.gz tarball as /tmp/my_project.tar.gz : ::

        git_archive('my_project')

    * Adding prefix in the archive so that a top directory will be extracted
      and all the files will remain inside it : ::

        git_archive('my_project', prefix='MyProject/')

    * Using outside a cloned repository : ::

        git_archive('my_project', project_path='/path/to/my_project')

    * Specify the tag to export. Default is the HEAD of master : ::

        git_archive('my_project', tag="1.2")

    * Change the format. Now this will create a file /tmp/my_project.zip : ::

        git_archive('my_project', format="zip")

    * Change the saving path. This will a create a file
      /home/django/my_project.zip : ::

        git_archive('my_project', path='/home/django')

    * Using a remote repository : ::

        git_archive('my_project',
        remote="git@git.u-strasbg.fr:django-ldapuds.git")

    """

    if format not in ('tar', 'tar.gz', 'zip'):
        fabric.api.abort('Git archive format not supported: %s' % format)

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
        with fabric.api.lcd(project_path):
            fabric.api.local(command % (options_build, tag))
    else:
        fabric.api.local(command % (options_build, tag))

    return os.path.join(path, filename)
