import sys
import os

class Template(object):

    # Subclasses must define:
    # _template_dir
    
    def module_dir(self):
        """
        Returns the module directory of this template.
        """
        mod = sys.modules(self.__class__.__name__)

    def template_dir(self):
        return os.path.join(self.module_dir(), self._template_dir)


class BasicPackage(Template):
    _template_dir = 'templates/basic_package'

class ZPT(Template):
    _template_dir = 'templates/zpt'

class WebKit(Template):
    _template_dir = 'templates/webkit'
    
class PasteDeploy(Template):
    _template_dir = 'templates/paste_deploy'
    
