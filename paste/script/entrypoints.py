import textwrap
import os
import pkg_resources
from command import Command, BadCommand
import fnmatch
import re

class EntryPointCommand(Command):

    usage = "ENTRY_POINT"
    summary = "Show information about an entry point"
    max_args = 1

    parser = Command.standard_parser(verbose=False)
    parser.add_option('--list', '-l',
                      dest='list_entry_points',
                      action='store_true',
                      help='List all the kinds of entry points on the system')
    parser.add_option('--egg', '-e',
                      dest='show_egg',
                      help="Show all the entry points for the given Egg")
    parser.add_option('--regex',
                      dest='use_regex',
                      action='store_true',
                      help="Make pattern match as regular expression, not just a wildcard pattern")

    def command(self):
        if self.options.list_entry_points:
            return self.list_entry_points()
        if self.options.show_egg:
            return self.show_egg()
        if not self.args:
            raise BadCommand("You must give an entry point (or --list)")
        pattern = self.get_pattern(self.args[0])
        groups = self.get_groups_by_pattern(pattern)
        if not groups:
            raise BadCommand('No group matched %s' % self.args[0])
        for group in groups:
            desc = self.get_group_description(group)
            print '[%s]' % group
            if desc:
                print self.wrap(desc)
                print
            by_dist = {}
            for ep in pkg_resources.iter_entry_points(group):
                by_dist.setdefault(ep.dist, []).append(ep)
            dists = by_dist.items()
            dists.sort(lambda a, b: cmp(str(a), str(b)))
            for dist, eps in dists:
                print '%s' % dist
                eps.sort(lambda a, b: cmp(a.name, b.name))
                longest_name = max([len(ep.name) for ep in eps])
                for ep in eps:
                    print '  %s%s = %s' % (
                        ep.name, ' '*(longest_name-len(ep.name)),
                        ep.module_name)
                    desc = self.get_entry_point_description(ep, group)
                    if desc and desc.description:
                        print self.wrap(desc.description, indent=4)

    def wrap(self, text, indent=0):
        text = textwrap.dedent(text)
        width = int(os.environ.get('COLUMNS', 70)) - indent
        lines = [
            ' '*indent+line for line in textwrap.wrap(text, width)]
        return '\n'.join(lines)

    def get_pattern(self, s):
        if not s:
            return None
        if self.options.use_regex:
            return re.compile(s)
        else:
            return re.compile(fnmatch.translate(s), re.I)

    def list_entry_points(self):
        pattern = self.get_pattern(self.args and self.args[0])
        groups = self.get_groups_by_pattern(pattern)
        print '%i entry point groups found:' % len(groups)
        for group in groups:
            desc = self.get_group_description(group)
            print '[%s]' % group
            if desc:
                print self.wrap(desc.description, indent=2)

    def get_groups_by_pattern(self, pattern):
        ws = pkg_resources.working_set
        eps = {}
        for dist in ws:
            for name in pkg_resources.get_entry_map(dist):
                if pattern and not pattern.search(name):
                    continue
                if (not pattern
                    and name.startswith('paste.description.')):
                    continue
                eps[name] = None
        eps = eps.keys()
        eps.sort()
        return eps
    
    def get_group_description(self, group):
        for entry in pkg_resources.iter_entry_points('paste.entry_point_description'):
            if entry.name == group:
                return entry.load()
        return None

    def get_entry_point_description(self, ep, group):
        meta_group = 'paste.description.'+group
        meta = ep.dist.get_entry_info(meta_group, ep.name)
        if not meta:
            generic = list(pkg_resources.iter_entry_points(
                meta_group, 'generic'))
            if not generic:
                return SuperGeneric(ep.load())
            # @@: Error if len(generic) > 1?
            print generic
            obj = generic[0].load()
            desc = obj(ep, group)
        else:
            desc = meta.load()
        return desc
    
class EntryPointDescription(object):

    def __init__(self, group):
        self.group = group

    # Should define:
    # * description

class MetaEntryPointDescription(object):

    description = """
    This is an entry point that describes other entry points.
    """

class SuperGeneric(object):

    def __init__(self, doc_object):
        self.doc_object = doc_object
        self.description = self.doc_object.__doc__

def super_generic(obj):
    desc = SuperGeneric(obj)
    if not desc.description:
        return None
    return desc
