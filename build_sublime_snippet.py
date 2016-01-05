#!/usr/bin/env python
import os
import platform
import shutil

from pydiploy.version import __version__

"""
    This script generate a sublime text snippet using
    pydiploy/examples/django_fabfile and then copy the file in sublime text
    config dir to use it directly.

"""


def copyFile(src, dest):
    """ Copy file from src to dest """
    try:
        shutil.copy(src, dest)
    except shutil.Error as e:
        print('Error: %s' % e)
    except IOError as e:
        print('Error: %s' % e.strerror)


def install_snippet(dest_filename, app_type):
    """ install snippets """
    # TODO manage other os (Darwin,windoz...)
    if platform.system() == "Linux":
        sublime_config_dirs = [
            '.config/sublime-text-3/Packages/User',
            '.config/sublime-text-2/Packages/User']
        for dir in sublime_config_dirs:
            dir = os.path.join(os.environ['HOME'], dir)
            if os.path.isdir(dir):
                copyFile(dest_filename, dir)
                print('Snippet for %s app installed in %s' % (app_type, dir))


def django_app():
    # Django snippets
    src_filename = 'pydiploy/examples/django_fabfile.py'
    dest_filename = 'tools/pydiployfabfile.sublime-snippet'

    source = open(src_filename, 'r')
    target = open(dest_filename, 'w')

    snippet_header = '<snippet>\n<content><![CDATA[\n'
    snippet_footer = '\n]]></content>\n<description>Pydiploy fabfile %s</description>\n<tabTrigger>pydiployfab</tabTrigger>\n<scope>source.python</scope>\n</snippet>' % __version__

    target.write(snippet_header)
    target.write(source.read())
    target.write(snippet_footer)
    source.close()
    target.close()

    install_snippet(dest_filename, "django")


def simple_app():
    # Simple snippets
    src_filename = 'pydiploy/examples/simple_fabfile.py'
    dest_filename = 'tools/pydiployfabfilesimple.sublime-snippet'

    source = open(src_filename, 'r')
    target = open(dest_filename, 'w')

    snippet_header = '<snippet>\n<content><![CDATA[\n'
    snippet_footer = '\n]]></content>\n<description>Pydiploy fabfile simple %s</description>\n<tabTrigger>pydiployfabsimple</tabTrigger>\n<scope>source.python</scope>\n</snippet>' % __version__

    target.write(snippet_header)
    target.write(source.read())
    target.write(snippet_footer)
    source.close()
    target.close()

    install_snippet(dest_filename, "simple")


def bottle_app():
    # bottle snippets
    src_filename = 'pydiploy/examples/bottle_fabfile.py'
    dest_filename = 'tools/pydiployfabfilebottle.sublime-snippet'

    source = open(src_filename, 'r')
    target = open(dest_filename, 'w')

    snippet_header = '<snippet>\n<content><![CDATA[\n'
    snippet_footer = '\n]]></content>\n<description>Pydiploy fabfile bottle %s</description>\n<tabTrigger>pydiployfabbottle</tabTrigger>\n<scope>source.python</scope>\n</snippet>' % __version__

    target.write(snippet_header)
    target.write(source.read())
    target.write(snippet_footer)
    source.close()
    target.close()

    install_snippet(dest_filename, "bottle")


def main():
    django_app()
    simple_app()
    bottle_app()




if __name__ == '__main__':
    main()
