PasteScript is a pluggable command-line tool.

**Note**: Paste Script is being maintained on life support. That
means that critical bugs will be fixed, and support for new versions
of Python will be handled, but other than that new features are not
being considered.

**With version 3.6.0 pastescript development moves to the pasteorg GitHub
organization and will be going deeper into maintenance mode unless
more active maintainers step forward to take over. "Deeper" in this
case means that releases will be much less frequent and patches
will only be accepted for security issues or major problems. Current
consumers of pastescript should prepare to migrate away to more modern
solutions.**

It includes some built-in features;

* Create file layouts for packages.  For instance, ``paster create
  --template=basic_package MyPackage`` will create a `setuptools
  <https://pythonhosted.org/setuptools/>`_-ready
  file layout.

* Serving up web applications, with configuration based on
  `paste.deploy <https://docs.pylonsproject.org/projects/pastedeploy>`_.

The latest version is available in a `GitHub repository
<https://github.com/pasteorg/pastescript/>`_.

For the latest changes see the `news file
<https://pastescript.readthedocs.io/en/latest/news.html>`_.
