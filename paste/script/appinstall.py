"""
Provides the two commands for preparing an application:
``prepare-app`` and ``setup-app``
"""

import os
from cStringIO import StringIO
from paste.script.command import Command, BadCommand
import paste.script.templates
from paste.script import copydir
import pkg_resources
from Cheetah.Template import Template
from ConfigParser import ConfigParser
from simpleconfig import load_flat_config

class AbstractInstallCommand(Command):

    #@classmethod
    def standard_parser(cls, sys_config=True, **kw):
        parser = super(AbstractInstallCommand, cls).standard_parser(**kw)
        if sys_config:
            parser.add_option('--sys-config',
                              action="append",
                              dest="sys_configs",
                              help="System configuration file")
        parser.add_option(
            '--easy-install',
            action='append',
            dest='easy_install_op',
            metavar='OP',
            help='an option to add if invoking easy_install (like --easy-install=exclude-scripts)')

        return parser


    standard_parser = classmethod(standard_parser)

    def load_sys_config(self):
        fns = self.default_configs() + (self.options.sys_configs or [])
        s = self.sys_config = {}
        for fn in fns:
            if os.path.exists(fn):
                s.update(load_flat_config(fn))
        return s

    def default_configs(self):
        inis = [os.path.join(os.path.dirname(__file__), 'paste-deploy.ini'),
                "/etc/paste/deploy.ini",
                "/usr/local/etc/paste/deploy.ini"]
        if 'HOME' in os.environ:
            inis.append(os.path.join(os.environ['HOME'],
                                     '.paste-deploy.ini'))
        if 'PASTE_POLICY' in os.environ:
            inis.append(os.environ['PASTE_POLICY'])
        return inis

    def get_distribution(self, req):
        try:
            dist = pkg_resources.get_distribution(req)
            if self.verbose:
                print 'Distribution already installed:'
                print ' ', dist, 'from', dist.location
            return dist
        except pkg_resources.DistributionNotFound:
            options = ['-v', '-m']
            for op in self.options.easy_install_op or []:
                if not op.startswith('-'):
                    op = '--'+op
                options.append(op)
            if self.simulate:
                raise BadCommand(
                    "Must install %s, but in simulation mode" % req)
            print "Must install %s" % req
            from setuptools.command import easy_install
            from setuptools import setup
            setup(script_args=['-q', 'easy_install']
                  + options + [req])
            return pkg_resources.get_distribution(req)

    def get_installer(self, distro, ep_group, ep_name):
        installer_class = distro.load_entry_point(
            'paste.app_install', ep_name)
        installer = installer_class(
            distro, ep_group, ep_name)
        return installer
    

class PrepareCommand(AbstractInstallCommand):

    default_verbosity = 1
    max_args = None
    min_args = 1
    summary = "Install a package and create a fresh config file"
    usage = "PACKAGE_NAME [VAR=VALUE]"

    parser = AbstractInstallCommand.standard_parser(
        simulate=True, quiet=True, interactive=True)
    parser.add_option('--info',
                      action="store_true",
                      dest="show_info",
                      help="Show information on the package (after installing it), but do not write a config file.")
    parser.add_option('--name',
                      action='store',
                      dest='ep_name',
                      help='The name of the application contained in the distribution (default "main")')
    parser.add_option('--entry-group',
                      action='store',
                      dest='ep_group',
                      default='paste.app_factory',
                      help='The entry point group to install (i.e., the kind of application; default paste.app_factory')

    def command(self):
        self.load_sys_config()
        self.requirement = self.args[0]
        if '#' in self.requirement:
            assert self.options.ep_name is None
            self.requirement, self.options.ep_name = self.requirement.split('#', 1)
        if not self.options.ep_name:
            self.options.ep_name = 'main'
        self.distro = self.get_distribution(self.requirement)
        self.installer = self.get_installer(
            self.distro, self.options.ep_group, self.options.ep_name)
        if self.options.show_info:
            if len(self.args) > 1:
                raise BadCommand(
                    "With --info you can only give one "
                    "argument")
            return self.show_info()
        if len(self.args) < 2:
            raise BadCommand(
                "You must give a configuration filename")
        self.config_file = self.args[1]
        self.project_name = self.distro.project_name
        self.vars = self.parse_vars(self.args[2:])
        self.vars['project_name'] = self.project_name
        self.vars['requirement'] = self.requirement
        self.vars['ep_name'] = self.options.ep_name
        self.vars['ep_group'] = self.options.ep_group
        self.vars.setdefault('app_name', self.project_name.lower())
        self.sys_config.update(self.vars)
        self.installer.write_config(self, self.config_file, self.vars)

    def show_info(self):
        text = self.installer.description(None)
        print text
        
class SetupCommand(AbstractInstallCommand):

    default_verbosity = 1
    max_args = 1
    min_args = 1
    summary = "Setup an application, given a config file"
    usage = "CONFIG_FILE"

    parser = AbstractInstallCommand.standard_parser(
        simulate=True, quiet=True, interactive=True)
    parser.add_option('--name',
                      action='store',
                      dest='section_name',
                      default='main',
                      help='The name of the section to set up (default: app:main)')

    def command(self):
        config_spec = self.args[0]
        section = self.options.section_name
        if not ':' in section:
            section = 'app:'+section
        if not config_spec.startswith('config:'):
            config_spec = 'config:' + config_spec
        config_file = config_spec[len('config:'):]
        conf = appconfig(config_file, relative_to=os.getcwd())
        ep_name = conf.context.entry_point_name
        ep_group = conf.context.protocol
        dist = conf.context.distribution
        installer = self.get_installer(dist, ep_group, ep_name)
        installer.setup_config(
            self, config_file, section, self.load_sys_config())
        
        
class Installer(object):

    """
    Abstract base class for installers, and also a generic
    installer that will run off config files in the .egg-info
    directory of a distribution.
    """

    def __init__(self, dist, ep_group, ep_name):
        self.dist = dist
        self.ep_group = ep_group
        self.ep_name = ep_name

    def description(self, config):
        return 'An app'

    def write_config(self, command, filename, sys_config):
        command.ensure_file(filename, 'test')

    def setup_config(self, command, filename, section, sys_config):
        pass
    
