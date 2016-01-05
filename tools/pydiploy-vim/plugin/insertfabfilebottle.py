try:
    import pydiploy
    import vim
    import string

    fabile = string.join(vim.current.buffer, "\n")
    fabfile = pydiploy.prepare.generate_fabfile_bottle()

    filename = vim.current.buffer.name

    f = open(filename, 'w')
    f.write(fabfile)
    f.close()

    print "Fabfile for bottle app written to "+filename

except ImportError, e:
    print "Pydiploy package not installed, please run: pip install pydiploy"
