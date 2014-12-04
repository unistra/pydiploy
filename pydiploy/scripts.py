#!/usr/bin/env python
import platform
from os.path import dirname, expanduser, isdir, join
from sys import stdout

from pydiploy.version import __version__
from six import StringIO

"""
    This script generate a sublime text snippet using
    pydiploy/examples/django_fabfile and then copy the file in sublime text
    config dir to use it directly.

"""

SUBLIME_SNIPPET_FILENAME = 'pydiployfabfile.sublime-snippet'
# TODO manage other os (Darwin,windoz...)
SUBLIME_CONFIG_DIRS = {
    'Linux' : [
        '.config/sublime-text-3/Packages/User',
        '.config/sublime-text-2/Packages/User'
    ],
}


def get_dest_files(system):
    try:
        return (join(expanduser('~'), cfg_dir, SUBLIME_SNIPPET_FILENAME)
                for cfg_dir in SUBLIME_CONFIG_DIRS[system])
    except KeyError:
        raise NotImplementedError(system)


def sublime_text_snippet():

    src_filename = join(dirname(__file__), 'examples', 'django_fabfile.py')

    stream = StringIO()

    snippet_header = '<snippet>\n<content><![CDATA[\n'
    snippet_footer = '\n]]></content>\n<description>Pydiploy fabfile %s</description>\n<tabTrigger>pydiployfab</tabTrigger>\n<scope>source.python</scope>\n</snippet>' % __version__

    stream.write(snippet_header)
    with open(src_filename, 'r') as src_h:
        stream.write(src_h.read())
    stream.write(snippet_footer)

    stream_content = stream.getvalue()
    for conf_file in get_dest_files(platform.system()):
        if isdir(dirname(conf_file)):
            with open(conf_file, 'w') as fh:
                fh.write(stream_content)
            stdout.write('Snippet installed at %s\n' % conf_file)

    stream.close()
