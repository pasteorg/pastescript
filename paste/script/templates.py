import sys
import os
import re

class Template(object):

    # Subclasses must define:
    # _template_dir (or template_dir())
    # summary

    # Variables this template uses (mostly for documentation now)
    # a list of instances of var()
    vars = []

    # Eggs that should be added as plugins:
    egg_plugins = []

    def __init__(self, name):
        self.name = name
    
    def module_dir(self):
        """
        Returns the module directory of this template.
        """
        mod = sys.modules[self.__class__.__module__]
        return os.path.dirname(mod.__file__)

    def template_dir(self):
        assert self._template_dir is not None, (
            "Template %r didn't set _template_dir" % self)
        return os.path.join(self.module_dir(), self._template_dir)

    def pre(self, command, output_dir, vars):
        """
        Called before template is applied.
        """
        pass

    def post(self, command, output_dir, vars):
        """
        Called after template is applied.
        """
        pass

    def insert_into_file(self, filename, marker_name, text,
                         indent=False, command=None):
        """
        Inserts ``text`` into the file, right after the given marker.
        Markers look like: ``-*- <marker_name>[:]? -*-``, and the text
        will go on the immediately following line.

        Raises ``ValueError`` if the marker is not found.

        If ``indent`` is true, then the text will be indented at the
        same level as the marker.

        If ``command`` is given, then notification messages will be
        given, and simulate obeyed.
        """
        if not text.endswith('\n'):
            raise ValueError(
                "The text must end with a newline: %r" % text)
        f = open(filename)
        lines = f.readlines()
        f.close()
        regex = re.compile(r'-\*-\s+%s:?\s+-\*-' % re.escape(marker_name),
                           re.I)
        for i in range(len(lines)):
            if regex.search(lines[i]):
                # Found it!
                if indent:
                    text = text.lstrip()
                    match = re.search(r'^[ \t]*', lines[i])
                    text = match.group(0) + text
                lines[i+1:i+1] = [text]
                break
        else:
            raise ValueError(
                "Marker '-*- %s -*-' not found in %s"
                % (marker_name, filename))
        if command and command.verbose:
            print 'Updating %s' % command.shorten(filename)
        if command and not command.simulate:
            f = open(filename, 'w')
            f.write(''.join(lines))
            f.close()

class var(object):

    def __init__(self, name, description,
                 default=''):
        self.name = name
        self.description = description
        self.default = default

class BasicPackage(Template):

    _template_dir = 'templates/basic_package'
    summary = "A basic setuptools-enabled package"
    vars = [
        var('version', 'Version (like 0.1)'),
        var('description', 'One-line description of the package'),
        var('long_description', 'Multi-line description (in reST)'),
        var('keywords', 'Space-separated keywords/tags'),
        var('author', 'Author name'),
        var('author_email', 'Author email'),
        var('url', 'URL of homepage'),
        var('license_name', 'License name'),
        var('zip_safe', 'True/False: if the package can be distributed as a .zip file', default=False),
        ]
    
