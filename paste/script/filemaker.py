# (c) 2005 Ian Bicking and contributors; written for Paste (http://pythonpaste.org)
# Licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
import os
import glob
from paste.script import pluginlib, copydir
from paste.script.command import BadCommand
try:
    import subprocess
except ImportError:
    from paste.script.util import subprocess24 as subprocess

class FileOp(object):
    """
    Enhance the ease of file copying/processing from a package into a target
    project
    """
    
    def __init__(self, simulate=False, 
                       verbose=True, 
                       interactive=True,
                       source_dir=None,
                       template_vars={}):
        """
        Initialize our File operation helper object
        
        source_dir
            Should refer to the directory within the package
            that contains the templates to be used for the other copy
            operations. It is assumed that packages will keep all their
            templates under a hierarchy starting here.
          
            This should be an absolute path passed in, for example::
          
                FileOp(source_dir=os.path.dirname(__file__) + '/templates')
        """
        self.simulate=simulate
        self.verbose = verbose
        self.interactive = interactive
        self.template_vars = template_vars
        self.source_dir = source_dir
    
    def copy_file(self, template, dest, filename=None, add_py=True):
        """
        Copy a file from the source location to somewhere in the
        destination.
        
        template
            The filename underneath self.source_dir to copy/process
        dest
            The destination directory in the project relative to where
            this command is being run
        filename
            What to name the file in the target project, use the same name
            as the template if not provided
        add_py
            Add a .py extension to all files copied
        """
        if not filename:
            filename = template.split('/')[0]
            if filename.endswith('_tmpl'):
                filename = filename[:-5]
        base_package, cdir = self.find_dir(dest)
        self.template_vars['base_package'] = base_package
        content = self.load_content(base_package, cdir, filename, template)
        if add_py:
            # @@: Why is it a default to add a .py extension? 
            filename = '%s.py' % filename
        dest = os.path.join(cdir, filename)
        self.ensure_file(dest, content)
    
    def copy_dir(self, template_dir, dest, destname=None):
        """
        Copy a directory recursively, processing any files within it
        that need to be processed (end in _tmpl).
        
        template_dir
            Directory under self.source_dir to copy/process
        dest
            Destination directory into which this directory will be copied
            to.
        destname
            Use this name instead of the original template_dir name for
            creating the directory
        """
        # @@: This should actually be implemented
        pass  

    def load_content(self, base_package, base, name, template):
        blank = os.path.join(base, name + '.py')
        if not os.path.exists(blank):
            blank = os.path.join(self.source_dir,
                                 template)
        f = open(blank, 'r')
        content = f.read()
        f.close()
        if blank.endswith('_tmpl'):
            content = copydir.substitute_content(content, self.template_vars,
                                                 filename=blank)
        return content

    def find_dir(self, dirname):
        egg_info = pluginlib.find_egg_info_dir(os.getcwd())
        # @@: Should give error about egg_info when top_level.txt missing
        f = open(os.path.join(egg_info, 'top_level.txt'))
        packages = [l.strip() for l in f.readlines()
                    if l.strip() and not l.strip().startswith('#')]
        f.close()
        # @@: This doesn't support deeper servlet directories,
        # or packages not kept at the top level.
        base = os.path.dirname(egg_info)
        possible = []
        for pkg in packages:
            d = os.path.join(base, pkg, dirname)
            if os.path.exists(d):
                possible.append((pkg, d))
        if not possible:
            self.ensure_dir(os.path.join(base, pkg, dirname))
            return self.find_dir(dirname)
        if len(possible) > 1:
            raise BadCommand(
                "Multiple %s dirs found (%s)" % (dirname, possible))
        return possible[0]
    
    def parse_path_name_args(self, name):
        """
        Given the name, assume that the first argument is a path/filename
        combination. Return the name and dir of this. If the name ends with
        '.py' that will be erased.
        
        Examples:
            comments             ->          comments, ''
            admin/comments       ->          comments, 'admin'
            h/ab/fred            ->          fred, 'h/ab'
        """
        if name.endswith('.py'):
            # Erase extensions
            name = name[:-3]
        if '.' in name:
            # Turn into directory name:
            name = name.replace('.', os.path.sep)
        if '/' != os.path.sep:
            name = name.replace('/', os.path.sep)
        parts = name.split(os.path.sep)
        name = parts[-1]
        if not parts[:-1]:
            dir = ''
        elif len(parts[:-1]) == 1:
            dir = parts[0]
        else:
            dir = os.path.join(*parts[:-1])
        return name, dir
    
    def ensure_dir(self, dir, svn_add=True):
        """
        Ensure that the directory exists, creating it if necessary.
        Respects verbosity and simulation.

        Adds directory to subversion if ``.svn/`` directory exists in
        parent, and directory was created.
        """
        dir = dir.rstrip(os.sep)
        if not dir:
            # we either reached the parent-most directory, or we got
            # a relative directory
            # @@: Should we make sure we resolve relative directories
            # first?  Though presumably the current directory always
            # exists.
            return
        if not os.path.exists(dir):
            self.ensure_dir(os.path.dirname(dir))
            if self.verbose:
                print 'Creating %s' % self.shorten(dir)
            if not self.simulate:
                os.mkdir(dir)
            if (svn_add and
                os.path.exists(os.path.join(os.path.dirname(dir), '.svn'))):
                self.run_command('svn', 'add', dir)
        else:
            if self.verbose > 1:
                print "Directory already exists: %s" % self.shorten(dir)

    def ensure_file(self, filename, content, svn_add=True):
        """
        Ensure a file named ``filename`` exists with the given
        content.  If ``--interactive`` has been enabled, this will ask
        the user what to do if a file exists with different content.
        """
        global difflib
        self.ensure_dir(os.path.dirname(filename), svn_add=svn_add)
        if not os.path.exists(filename):
            if self.verbose:
                print 'Creating %s' % filename
            if not self.simulate:
                f = open(filename, 'wb')
                f.write(content)
                f.close()
            if svn_add and os.path.exists(os.path.join(os.path.dirname(filename), '.svn')):
                self.run_command('svn', 'add', filename)
            return
        f = open(filename, 'rb')
        old_content = f.read()
        f.close()
        if content == old_content:
            if self.verbose > 1:
                print 'File %s matches expected content' % filename
            return
        if not self.options.overwrite:
            print 'Warning: file %s does not match expected content' % filename
            if difflib is None:
                import difflib
            diff = difflib.context_diff(
                content.splitlines(),
                old_content.splitlines(),
                'expected ' + filename,
                filename)
            print '\n'.join(diff)
            if self.interactive:
                while 1:
                    s = raw_input(
                        'Overwrite file with new content? [y/N] ').strip().lower()
                    if not s:
                        s = 'n'
                    if s.startswith('y'):
                        break
                    if s.startswith('n'):
                        return
                    print 'Unknown response; Y or N please'
            else:
                return
                    
        if self.verbose:
            print 'Overwriting %s with new content' % filename
        if not self.simulate:
            f = open(filename, 'wb')
            f.write(content)
            f.close()

    def shorten(self, fn, *paths):
        """
        Return a shorted form of the filename (relative to the current
        directory), typically for displaying in messages.  If
        ``*paths`` are present, then use os.path.join to create the
        full filename before shortening.
        """
        if paths:
            fn = os.path.join(fn, *paths)
        if fn.startswith(os.getcwd()):
            return fn[len(os.getcwd()):].lstrip(os.path.sep)
        else:
            return fn

    def run_command(self, cmd, *args, **kw):
        """
        Runs the command, respecting verbosity and simulation.
        Returns stdout, or None if simulating.
        """
        cwd = popdefault(kw, 'cwd', os.getcwd())
        capture_stderr = popdefault(kw, 'capture_stderr', False)
        expect_returncode = popdefault(kw, 'expect_returncode', False)
        assert not kw, ("Arguments not expected: %s" % kw)
        if capture_stderr:
            stderr_pipe = subprocess.STDOUT
        else:
            stderr_pipe = subprocess.PIPE
        try:
            proc = subprocess.Popen([cmd] + list(args),
                                    cwd=cwd,
                                    stderr=stderr_pipe,
                                    stdout=subprocess.PIPE)
        except OSError, e:
            if e.errno != 2:
                # File not found
                raise
            raise OSError(
                "The expected executable %s was not found (%s)"
                % (cmd, e))
        if self.verbose:
            print 'Running %s %s' % (cmd, ' '.join(args))
        if self.simulate:
            return None
        stdout, stderr = proc.communicate()
        if proc.returncode and not expect_returncode:
            if not self.verbose:
                print 'Running %s %s' % (cmd, ' '.join(args))
            print 'Error (exit code: %s)' % proc.returncode
            if stderr:
                print stderr
            raise OSError("Error executing command %s" % cmd)
        if self.verbose > 2:
            if stderr:
                print 'Command error output:'
                print stderr
            if stdout:
                print 'Command output:'
                print stdout
        return stdout

def popdefault(dict, name, default=None):
    if name not in dict:
        return default
    else:
        v = dict[name]
        del dict[name]
        return v

