from setuptools import setup, find_packages

version = '0.1'

setup(
    name="PasteScript",
    version=version,
    description="A pluggable command-line frontend, including commands to setup package file layouts",
    long_description="""\
This is a pluggable command-line tool.

It includes some built-in features;

* Create file layouts for packages.  For instance, ``paste create
  --template=basic_package MyPackage`` will create a `setuptools
  <http://peak.telecommunity.com/DevCenter/setuptools>`_-ready
  file layout.

* Serving up web applications, with configuration based on
  `paste.deploy <http://pythonpaste.org/deploy/paste-deploy.html>`_.
    
See also the `Subversion repository <http://svn.pythonpaste.org/Paste/Script/trunk#egg=Paste-Script-%sdev>`_
""" % version,
    classifiers=[
      "Development Status :: 4 - Beta",
      "Intended Audience :: Developers",
      "License :: OSI Approved :: MIT License"
      "Programming Language :: Python",
      "Topic :: Internet :: WWW/HTTP",
      "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
      "Topic :: Software Development :: Libraries :: Python Modules",
      ],
    keywords='web wsgi setuptools framework command-line setup',
    author="Ian Bicking",
    author_email="ianb@colorstudy.com",
    url="http://pythonpaste.org/script/script.html",
    namespace_packages=['paste'],
    packages=find_packages(exclude='tests'),
    package_data={
      'paste.script': ['templates/basic_package/setup.*',
                       'templates/basic_package/tests/*.py',
                       # @@: docs/ doesn't have any files :(
                       'templates/basic_package/+package+/*.py'],
      },
    zip_safe=False,
    scripts=['scripts/paster'],
    extras_require={
      'Templating': [],
      'Cheetah': ['Cheetah'],
      'Config': ['PasteDeploy'],
      'WSGIUtils': ['WSGIUtils'],
      'Flup': ['Flup'],
      # the Paste feature means the complete set of features;
      # (other features are truly optional)
      'Paste': ['PasteDeploy', 'Cheetah'],
      },
    entry_points="""
    [paste.global_paster_command]
    help=paste.script.help:HelpCommand
    create=paste.script.create_distro:CreateDistroCommand [Templating]
    serve=paste.script.serve:ServeCommand [Config]
    exe=paste.script.exe:ExeCommand

    [paste.paster_create_template]
    basic_package=paste.script.templates:BasicPackage

    [paste.server_runner]
    wsgiutils=paste.script.wsgiutils_server:run_server [WSGIUtils]
    flup_ajp_thread=paste.script.flup_server:run_ajp_thread [Flup]
    flup_ajp_fork=paste.script.flup_server:run_ajp_fork [Flup]
    flup_fcgi_thread=paste.script.flup_server:run_fcgi_thread [Flup]
    flup_fcgi_fork=paste.script.flup_server:run_fcgi_fork [Flup]
    flup_scgi_thread=paste.script.flup_server:run_scgi_thread [Flup]
    flup_scgi_fork=paste.script.flup_server:run_scgi_fork [Flup]

    [paste.app_factory]
    test=paste.script.testapp:TestApplication
    """,
    )
