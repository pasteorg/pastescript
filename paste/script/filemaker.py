import os
import glob
from paste.script import pluginlib, copydir
from paste.script.command import BadCommand

class FileOp(object):
    """
    Enhance the ease of file copying/processing
    """
    
    def __init__(self, simulate=False, 
                       verbose=True, 
                       interactive=True,
                       source_dir=None,
                       template_vars={}):
        """
        Initialize our File operation helper object
        
        - source_dir should refer to the directory within the package
          that contains the templates to be used for the other copy
          operations. It is assumed that packages will keep all their
          templates under a hierarchy starting here.
          
          This should be an absolute path passed in, for example:
            FileOp(source_dir=os.path.dirname(__file__) + '/templates')
        """
        self.simulate=simulate
        self.verbose = verbose
        self.interactive = interactive
        self.template_vars = template_vars
        self.source_dir = source_dir
    
    def copy_file(self, template, dest, filename):
        """
        Copy a file from the source location to somewhere in the
        destination.
        # THIS CAN LIKELY BE STREAMLINED...
        
        template - The filename underneat self.source_dir to copy/process
        dest - The destination directory in the project relative to where
               this command is being run
        filename - What to name the file when its copied
            # SHOULD BE OPTIONAL
        """
        base_package, cdir = self.find_dir(dest)
        self.template_vars['base_package'] = base_package
        content = self.load_content(base_package, cdir, filename, template)
        #raise Exception(cdir, destdir, '%s.py' % filename)
        dest = os.path.join(cdir, '%s.py' % filename)
        self.ensure_file(dest, content)

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
