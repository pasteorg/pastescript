import re
import sys
import os
import pkg_resources
from command import Command, BadCommand
import copydir
import pluginlib

class CreateDistroCommand(Command):

    usage = 'PACKAGE_NAME [VAR=VALUE VAR2=VALUE2 ...]'
    summary = "Create the file layout for a Python distribution"
    short_description = summary

    parser = Command.standard_parser(
        simulate=True)
    parser.add_option('-o', '--output-dir',
                      dest='output_dir',
                      metavar='DIR',
                      default='.',
                      help="Write put the directory into DIR")
    parser.add_option('--template-dir',
                      dest='template_dir',
                      metavar='DIR',
                      action='append',
                      help="Read template for output from DIR")
    parser.add_option('--svn-repository',
                      dest='svn_repository',
                      metavar='REPOS',
                      help="Create package at given repository location")
    parser.add_option('--list-templates',
                      dest='list_templates',
                      action='store_true',
                      help="List all templates available")
    parser.add_option('-t', '--template',
                      dest='templates',
                      metavar='TEMPLATE',
                      action='append',
                      help="Add a template to the create process")

    _bad_chars_re = re.compile('[^a-zA-Z0-9]')

    def command(self):
        if self.options.list_templates:
            self.list_templates()
            return
        if not self.args:
            raise BadCommand('You must provide a PACKAGE_NAME')
        templates = self.options.templates or []
        if 'basic_package' not in templates:
            templates.insert(0, 'basic_package')
        templates = map(self.get_template, templates)
        dist_name = self.args[0]
        pkg_name = self._bad_chars_re.sub('', dist_name.lower())
        vars = {'name': dist_name,
                'package': pkg_name,
                }
        vars.update(self.parse_vars(self.args[1:]))
        if self.verbose: # @@: > 1?
            self.display_vars(vars)

        output_dir = os.path.join(self.options.output_dir, dist_name)
        if self.options.svn_repository:
            self.setup_svn_repository(output_dir, dist_name)

        for template in templates:
            self.create_template(
                template, output_dir, vars)

        cmd = "cd %s ; %s setup.py egg_info" % (
            output_dir, sys.executable)
        if self.verbose:
            print 'Running %s' % cmd
        if not self.simulate:
            os.system(cmd)

        egg_info_dir = os.path.join(output_dir, '%s.egg-info' % dist_name)
        for template in templates:
            for spec in template.egg_plugins:
                if self.verbose:
                    print 'Adding %s to paster_plugins.txt' % spec
                if not self.simulate:
                    pluginlib.add_plugin(egg_info_dir, spec)
        
        if self.options.svn_repository:
            self.add_svn_repository(output_dir)

    def create_template(self, template, output_dir, vars):
        if self.verbose:
            print 'Creating template %s' % template.name
        template_dir = template.template_dir()
        copydir.copy_dir(template_dir, output_dir,
                         vars,
                         self.verbose,
                         self.options.simulate,
                         indent=1)

    def setup_svn_repository(self, output_dir, dist_name):
        # @@: Use subprocess
        svn_repos = self.options.svn_repository
        svn_repos_path = os.path.join(svn_repos, dist_name)
        cmd = '''\
svn mkdir %(svn_repos_path)s          \\
          %(svn_repos_path)s/trunk    \\
          %(svn_repos_path)s/tags     \\
          %(svn_repos_path)s/branches \\
    -m "New project %(dist_name)s"''' % {'svn_repos_path': svn_repos_path, 
                                         'dist_name': dist_name}
        if self.verbose:
            print "Running:"
            print cmd
        if not self.simulate:
            os.system(cmd)
        svn_repos_path_trunk = os.path.join(svn_repos_path,'trunk')
        cmd = 'svn co "%s" "%s"' % (svn_repos_path_trunk, output_dir)
        if self.verbose:
            print "Running %s" % cmd
        if not self.simulate:
            os.system(cmd)

    def add_svn_repository(self, output_dir):
        svn_repos = self.options.svn_repository
        cmd = 'svn add %s/*' % output_dir
        if self.verbose:
            print "Running %s" % cmd
        if not self.simulate:
            os.system(cmd)
        if self.verbose:
            print ("You must next run 'svn commit' to commit the "
                   "files to repository")
        


    def get_template(self, template_name):
        for entry in self.all_entry_points():
            if entry.name == template_name:
                return entry.load()(entry.name)
        raise LookupError(
            'Template by name %r not found' % template_name)

    def all_entry_points(self):
        if not hasattr(self, '_entry_points'):
            self._entry_points = list(pkg_resources.iter_entry_points(
            'paste.paster_create_template'))
        return self._entry_points

    def parse_vars(self, args):
        result = {}
        for arg in args:
            if '=' not in arg:
                raise BadCommand(
                    'Variable assignment %r invalid (no "=")'
                    % arg)
            name, value = arg.split('=', 1)
            result[name] = value
        return result

    def display_vars(self, vars):
        vars = vars.items()
        vars.sort()
        print 'Variables:'
        max_var = max([len(n) for n, v in vars])
        for name, value in vars:
            print '  %s:%s  %s' % (
                name, ' '*(max_var-len(name)), value)
        
    def list_templates(self):
        templates = []
        for entry in self.all_entry_points():
            templates.append(entry.load()(entry.name))
        max_name = max([len(t.name) for t in templates])
        templates.sort(lambda a, b: cmp(a.name, b.name))
        print 'Available templates:'
        for template in templates:
            # @@: Wrap description
            print '  %s:%s  %s' % (
                template.name,
                ' '*(max_name-len(template.name)),
                template.summary)
        
