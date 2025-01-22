# Procedure to release a new version:
#
# - run tests: run tox
# - update version in setup.py (version)
# - check that "python setup.py sdist" contains all files tracked by
#   the SCM (Mercurial): update MANIFEST.in if needed
# - update changelog: docs/news.txt
#
# - increment version in setup.py (version)
# - git commit
# - git tag -s VERSION
# - git push
# - python setup.py sdist bdist_wheel upload --sign

from setuptools import setup, find_packages
import os
import re
import sys

version = '3.7.0'

news = os.path.join(os.path.dirname(__file__), 'docs', 'news.txt')
found_news = ''
if os.path.exists(news):
    with open(news) as fp:
        news = fp.read()
    parts = re.split(r'([0-9\.]+)\s*\n\r?-+\n\r?', news)
    for i in range(len(parts)-1):
        if parts[i] == version:
            found_news = parts[i+i]
            break
if not found_news:
    print('Warning: no news for this version found', file=sys.stderr)

with open("README.rst") as fp:
    long_description = fp.read().strip()

if found_news:
    title = 'Changes in %s' % version
    long_description += "\n%s\n%s\n" % (title, '-'*len(title))
    long_description += found_news

setup(
    name="PasteScript",
    version=version,
    description="A pluggable command-line frontend, including commands to setup package file layouts",
    long_description=long_description,
    classifiers=[
      "Development Status :: 6 - Mature",
      "Intended Audience :: Developers",
      "License :: OSI Approved :: MIT License",
      "Programming Language :: Python :: 3",
      "Programming Language :: Python :: 3.8",
      "Programming Language :: Python :: 3.9",
      "Programming Language :: Python :: 3.10",
      "Programming Language :: Python :: 3.11",
      "Programming Language :: Python :: 3.12",
      "Programming Language :: Python :: 3.13",
      "Topic :: Internet :: WWW/HTTP",
      "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
      "Topic :: Software Development :: Libraries :: Python Modules",
      "Framework :: Paste",
      ],
    keywords='web wsgi setuptools framework command-line setup',
    author="Ian Bicking",
    author_email="ianb@colorstudy.com",
    url="https://pastescript.readthedocs.io/",
    namespace_packages=['paste'],
    license='MIT',
    python_requires='>=3.8',
    packages=find_packages(exclude=['tests','tests.*']),
    package_data={
      'paste.script': ['paster-templates/basic_package/setup.*',
                       'paster-templates/basic_package/tests/*.py',
                       # @@: docs/ doesn't have any files :(
                       'paster-templates/basic_package/+package+/*.py'],
      },
    zip_safe=False,
    extras_require={
      'Templating': [],
      'Cheetah': ['Cheetah'],
      'Config': ['PasteDeploy'],
      'WSGIUtils': ['WSGIserver'],
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
    request=paste.script.request:RequestCommand [Config]
    post=paste.script.request:RequestCommand [Config]
    exe=paste.script.exe:ExeCommand
    points=paste.script.entrypoints:EntryPointCommand
    make-config=paste.script.appinstall:MakeConfigCommand
    setup-app=paste.script.appinstall:SetupCommand

    [paste.paster_command]
    grep = paste.script.grep:GrepCommand

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
    cgi=paste.script.cgi_server:paste_run_cgi
    cherrypy=paste.script.cherrypy_server:cpwsgi_server
    twisted=paste.script.twisted_web2_server:run_twisted

    [paste.app_factory]
    test=paste.script.testapp:make_test_application

    [paste.entry_point_description]
    paste.entry_point_description = paste.script.epdesc:MetaEntryPointDescription
    paste.paster_create_template = paste.script.epdesc:CreateTemplateDescription
    paste.paster_command = paste.script.epdesc:PasterCommandDescription
    paste.global_paster_command = paste.script.epdesc:GlobalPasterCommandDescription
    paste.app_install = paste.script.epdesc:AppInstallDescription

    # These aren't part of Paste Script particularly, but
    # we'll document them here
    console_scripts = paste.script.epdesc:ConsoleScriptsDescription
    # @@: Need non-console scripts...
    distutils.commands = paste.script.epdesc:DistutilsCommandsDescription
    distutils.setup_keywords = paste.script.epdesc:SetupKeywordsDescription
    egg_info.writers = paste.script.epdesc:EggInfoWriters
    # @@: Not sure what this does:
    #setuptools.file_finders = paste.script.epdesc:SetuptoolsFileFinders

    [console_scripts]
    paster=paste.script.command:run

    [distutils.setup_keywords]
    paster_plugins = setuptools.dist:assert_string_list

    [egg_info.writers]
    paster_plugins.txt = setuptools.command.egg_info:write_arg
    """,
    install_requires=[
      'Paste>=3.0',
      'PasteDeploy',
      'setuptools',
      ],
    )
