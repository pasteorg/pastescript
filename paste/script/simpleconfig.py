"""
An even simpler configuration loader.  Very simple
"""
from initools import iniparser

__all__ = ['load_flat_config']

class _FlatParser(iniparser.INIParser):

    """
    An internal subclass of the abstract ini parser, which saves
    everything into one dictionary.
    """

    def reset(self):
        self.data = {}
        iniparser.INIParser.reset(self)

    def assignment(self, name, content):
        self.data[name] = content

    def new_section(self, section):
        self.parse_error(
            "System config files cannot have sections")

def load_flat_config(filename):
    p = _FlatParser()
    p.load(filename)
    return p.data
