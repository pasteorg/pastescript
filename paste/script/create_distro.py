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
        simulate=True, interactive=True)
    parser.add_option('-o', '--output-dir',
                      dest='output_dir',
                      metavar='DIR',
                      default='.',
                      help="Write put the directory into DIR")
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
        asked_tmpls = self.options.templates or ['basic_package']
        templates = []
        for tmpl_name in asked_tmpls:
            self.extend_templates(templates, tmpl_name)
        if self.verbose:
            print 'Selected and implied templates:'
            max_tmpl_name = max([len(tmpl_name) for tmpl_name, tmpl in templates])
            for tmpl_name, tmpl in templates:
                print '  %s%s  %s' % (
                    tmpl_name, ' '*(max_tmpl_name-len(tmpl_name)),
                    tmpl.summary)
        templates = [tmpl for name, tmpl in templates]
        dist_name = self.args[0]
        pkg_name = self._bad_chars_re.sub('', dist_name.lower())
        vars = {'project': dist_name,
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

        self.run_command(sys.executable, 'setup.py', 'egg_info',
                         cwd=output_dir)

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
        template.pre(self, output_dir, vars)
        copydir.copy_dir(template_dir, output_dir,
                         vars,
                         verbosity=self.verbose,
                         simulate=self.options.simulate,
                         interactive=self.options.interactive,
                         indent=1)
        template.post(self, output_dir, vars)

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

    def extend_templates(self, templates, tmpl_name):
        if '#' in tmpl_name:
            dist_name, tmpl_name = tmpl_name.split('#', 1)
        else:
            dist_name, tmpl_name = None, tmpl_name
        if dist_name is None:
            for entry in self.all_entry_points():
                if entry.name == tmpl_name:
                    tmpl = entry.load()(entry.name)
                    dist_name = entry.dist.project_name
                    break
            else:
                raise LookupError(
                    'Template by name %r not found' % tmpl_name)
        else:
            dist = pkg_resources.get_distribution(dist_name)
            entry = dist.get_entry_info(
                'paste.paster_create_template', tmpl_name)
            tmpl = entry.load()(entry.name)
        full_name = '%s#%s' % (dist_name, tmpl_name)
        for item_full_name, tmpl in templates:
            if item_full_name == full_name:
                # Already loaded
                return
        for req_name in tmpl.required_templates:
            self.extend_templates(templates, req_name)
        templates.append((full_name, tmpl))

    def all_entry_points(self):
        if not hasattr(self, '_entry_points'):
            self._entry_points = list(pkg_resources.iter_entry_points(
            'paste.paster_create_template'))
        return self._entry_points

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
        
