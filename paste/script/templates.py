import sys
import os

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
    
class ZPT(Template):

    _template_dir = 'templates/zpt'
    summary = "A Zope Page Template project"

class WebKit(Template):

    _template_dir = 'templates/webkit'
    summary = "A Paste WebKit web application"

    egg_plugins = ['PasteWebKit']
    
class PasteDeploy(Template):

    _template_dir = 'templates/paste_deploy'
    summary = "A web application deployed through paste.deploy"
    
    egg_plugins = ['PasteDeploy']
    
