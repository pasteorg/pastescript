import os
import glob
from paste.script import pluginlib, copydir

class FileOp(object):
    """
    Enhance the ease of file copying/processing
    """
    
    def __init__(self, simulate=False, 
                       verbose=True, 
                       interactive=True,
                       source_dir='templates'
                       template_vars={}):
        """
        Initialize our File operation helper object
        
        - source_dir should refer to the directory within the package
          that contains the templates to be used for the other copy
          operations. It is assumed that packages will keep all their
          templates under a hierarchy starting here.
        """
        self.simulate=simulate
        self.verbose = verbose
        self.interactive = interactive
        self.template_vars = template_vars
        self.source_dir = source_dir
    
    def copy_file(self, template, dest, filename, destdir):
        """
        Copy a file from the source location to somewhere in the
        destination.
        # THIS CAN LIKELY BE STREAMLINED...
        
        template - The filename underneat self.source_dir to copy/process
        dest - The destination directory in the project relative to where
               this command is being run
        filename - What to name the file when its copied
            # SHOULD BE OPTIONAL
        destdir - The directory within dest if this file should be nested
            # SHOULD BE CONSOLIDATED WITH DEST
        """
        base_package, cdir = self.find_dir(dest)
        self.template_vars['base_package'] = base_package
        content = self.load_content(base_package, cdir, destdir, filename, template)
        #raise Exception(cdir, destdir, '%s.py' % filename)
        dest = os.path.join(cdir, destdir, '%s.py' % filename)
        self.ensure_file(dest, content)

    def load_content(self, base_package, base, dir, name, template):
        blank = os.path.join(base, name + '.py')
        if not os.path.exists(blank):
            blank = os.path.join(os.path.dirname(__file__),
                                 self.source_dir,
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
            raise BadCommand(
                "No %s dir found (looked in %s)"
                % (dirname,', '.join(packages)))
        if len(possible) > 1:
            raise BadCommand(
                "Multiple %s dirs found (%s)" % (dirname, possible))
        return possible[0]
    
