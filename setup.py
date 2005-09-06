from setuptools import setup, find_packages

version = '0.1'

setup(
    name="PasteScript",
    version=version,
    description="A pluggable command-line frontend to commands for Paste applications",
    long_description="""\
See also the `Subversion repository <http://svn.pythonpaste.org/Paste/Script/trunk#egg=Paste-Script-%sdev>`_
""" % version,
    classifiers=["Development Status :: 3 - Alpha",
                 "Intended Audience :: Developers",
                 "License :: OSI Approved :: Python Software Foundation License",
                 "Programming Language :: Python",
                 "Topic :: Internet :: WWW/HTTP",
                 "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
                 "Topic :: Software Development :: Libraries :: Python Modules",
                 ],
    keywords='web wsgi application framework command-line framework',
    author="Ian Bicking",
    author_email="ianb@colorstudy.com",
    url="http://pythonpaste.org/script/script.html",
    namespace_packages=['paste'],
    packages=find_packages(exclude='tests'),
    zip_safe=True,
    scripts=['scripts/paster'],
    entry_points={
    'paste.paster_command': """
    help=paste.script.help:HelpCommand
    create=paste.script.create_distro:CreateDistroCommand
    serve=paste.script.serve:ServeCommand
    exe=paste.script.exe:ExeCommand
    """,
    'paste.paster_create_template': """
    basic_package=paste.script.templates:BasicPackage
    zpt=paste.script.templates:ZPT
    webkit=paste.script.templates:WebKit
    paste_deploy=paste.script.templates:PasteDeploy
    """,
    'paste.server_runner': """
    wsgiutils=paste.script.wsgiutils_server:run_server
    flup_ajp_thread=paste.script.flup_server:run_ajp_thread
    flup_ajp_fork=paste.script.flup_server:run_ajp_fork
    flup_fcgi_thread=paste.script.flup_server:run_fcgi_thread
    flup_fcgi_fork=paste.script.flup_server:run_fcgi_fork
    flup_scgi_thread=paste.script.flup_server:run_scgi_thread
    flup_scgi_fork=paste.script.flup_server:run_scgi_fork
    """,
    'paste.app_factory': """
    test=paste.script.testapp:TestApplication
    """,
    },
    install_requires=['PasteDeploy', 'Paste'],
    )
