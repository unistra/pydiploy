"""
"""


from fabric.api import local


def archive(path, tag="HEAD", remote="", prefix=""):
    """
    """
    options = ['--format=tar']
    if remote:
        options.append('--remote=%s' % remote)
    if prefix:
        options.append('--prefix=%s' % prefix)

    options_build = ' '.join(options)
    local('git archive %s %s |gzip > %s' % (options_build, tag, path))
