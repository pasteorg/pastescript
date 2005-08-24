import re
import sys
import os
from command import Command
import copydir

class CreateDistroCommand(Command):

    max_args = 1
    min_args = 1
    usage = 'PACKAGE_NAME'
    summary = "Create the file layout for a Python distribution"
    short_description = summary

    parser = Command.standard_parser(
        simulate=True)
    parser.add_option('-o', '--output-dir',
                      dest='output_dir',
                      metavar='DIR',
                      default='.',
                      help="Write put the directory into DIR")
    parser.add_option('--template',
                      dest='template',
                      metavar='DIR',
                      help="Read template for output from DIR")
    parser.add_option('--svn-repository',
                      dest='svn_repository',
                      metavar='REPOS',
                      help="Create package at given repository location")

    _vars = [
        ('version', 'X.Y'),
        ('description', 'TEXT'),
        ('long_description', 'TEXT'),
        ('keywords', 'SPACE_SEPARATED'),
        ('author', 'FULL_NAME'),
        ('author_email', 'EMAIL'),
        ('url', 'URL'),
        ('license', 'LICENSE_NAME'),
        ('zip_safe', 'TRUE/FALSE'),
        ]

    var_group = parser.add_option_group(
        'Optional values to generate setup.py arguments')
    for name, metavar in _vars:
        var_group.add_option('--%s' % name,
                             metavar=metavar,
                             dest=name)
    del var_group, name, metavar

    template = 'basic_template'

    _bad_chars_re = re.compile('[^a-zA-Z0-9]')

    def command(self):
        dist_name = self.args[0]
        pkg_name = self._bad_chars_re.sub('', dist_name.lower())
        vars = {'name': dist_name,
                'package': pkg_name,
                }
        output_dir = os.path.join(self.options.output_dir, dist_name)
        svn_repos = self.options.svn_repository
        if svn_repos:
            # @@: Use subprocess
            cmd = 'svn mkdir -m "New project %s" "%s"' % (
                dist_name, svn_repos)
            if self.verbose:
                print "Running %s" % cmd
            os.system(cmd)
            cmd = 'svn co "%s" "%s"' % (svn_repos, output_dir)
            if self.verbose:
                print "Running %s" % cmd
            os.system(cmd)
            
        for name, metavar in self._vars:
            vars[name] = getattr(self.options, name)
        template = self.options.template or self.template
        template = os.path.join(self.here(), template)
        copydir.copy_dir(template, output_dir,
                         vars,
                         self.verbose,
                         self.options.simulate)
        if svn_repos:
            cmd = 'svn add %s/*' % output_dir
            if self.verbose:
                print "Running %s" % cmd
            os.system(cmd)
            if self.verbose:
                print "You must run 'svn commit' to add files to repository"
        
