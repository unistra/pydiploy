# -*- coding: utf-8 -*-

"""

Git vcs relatives methods
=========================

"""

import os

import fabric
from pydiploy.decorators import do_verbose


@do_verbose
def archive(filename, path='/tmp', format="tar.gz", tag="HEAD", remote="",
            prefix="", project_path=".", specific_folder=""):
    """ Creates an archive from a git repository or directly from a project

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
    if specific_folder:
        command = 'git archive %s %s:' + specific_folder
    else:
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


@do_verbose
def collect_tags(project_path='.', remote=""):
    """ Collects tags names locally or from a remote repository """

    command = "git tag | sort -V"

    with fabric.context_managers.hide('running', 'stdout', 'stderr'):
        if not remote and project_path:
            with fabric.api.lcd(project_path):
                refs = fabric.api.local(command, capture=True)
        else:
            refs = fabric.api.local(command, capture=True)
        return refs.split('\n')


@do_verbose
def collect_branches(project_path='.', remote=""):
    """ Collects branches names locally or from a remote repository """

    command = "git branch | sort -V | sed -e 's/^\* //' -e 's/^  //'"

    with fabric.context_managers.hide('running', 'stdout', 'stderr'):
        if not remote and project_path:
            with fabric.api.lcd(project_path):
                refs = fabric.api.local(command, capture=True)
        else:
            refs = fabric.api.local(command, capture=True)
        return refs.split('\n')


@do_verbose
def check_tag_exist(tag=None):
    """ Checks if a tag/branch exists in the repository """
    if tag:
        if (tag not in collect_branches() and tag not in collect_tags()):
            return False
        return True
